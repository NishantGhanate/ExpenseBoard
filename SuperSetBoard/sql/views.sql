-- 1. Canonical Transaction Fact View
CREATE OR REPLACE VIEW v_fact_transactions AS
SELECT
    t.id AS transaction_id,
    t.transaction_date,
    u.name AS user_name,
    ba.number AS account_number,
    ba.type AS account_type,
    tt.name AS transaction_type, -- 'Credit' or 'Debit'
    t.amount,
    -- Core analytical field: Credits (+) and Debits (-)
    CASE WHEN tt.name = 'Debit' THEN -t.amount ELSE t.amount END AS signed_amount,
    
    -- WEALTH TRAJECTORY: Running total per user to show individual growth
    SUM(CASE WHEN tt.name = 'Debit' THEN -t.amount ELSE t.amount END) 
        OVER (PARTITION BY t.user_id ORDER BY t.transaction_date, t.id) AS running_wealth,
    
    c.name AS category_name,
    c.type AS category_group, -- 'INCOME' or 'EXPENSE'
    pm.name AS payment_method, 
    pm.type AS payment_type, -- ADDED: This is your UPI/Wallet/NetBanking/etc.
    tg.name AS tag_name,
    
    -- BUDGET DISCIPLINE: Helps calculate "Burn Rate" for essentials
    CASE WHEN tg.name = 'essential' THEN t.amount ELSE 0 END AS essential_spend,
    
    t.description,
    t.goal_id
FROM
    ss_transactions t
    LEFT JOIN ss_users u ON u.id = t.user_id
    LEFT JOIN ss_bank_accounts ba ON ba.id = t.bank_account_id
    LEFT JOIN ss_categories c ON c.id = t.category_id
    LEFT JOIN ss_transaction_types tt ON tt.id = t.type_id
    LEFT JOIN ss_payment_methods pm ON pm.id = t.payment_method_id
    LEFT JOIN ss_tags tg ON tg.id = t.tag_id
WHERE t.is_active = TRUE;

-- 2. Canonical Goal Actuals View
CREATE OR REPLACE VIEW v_fact_goal_performance AS
SELECT
    g.id AS goal_id,
    g.name AS goal_name,
    g.target_amount,
    g.start_date,
    g.target_date AS end_date,
    COALESCE(SUM(t.amount), 0) AS current_actual,
    (g.target_amount - COALESCE(SUM(t.amount), 0)) AS gap_remaining,
    ROUND(CASE WHEN g.target_amount > 0 THEN (SUM(t.amount) / g.target_amount) * 100 ELSE 0 END, 2) AS completion_pct,
    
    -- ANALYTICAL KPI: How much do you need to save per month starting today?
    CASE 
        WHEN g.target_date > CURRENT_DATE AND (g.target_amount - COALESCE(SUM(t.amount), 0)) > 0 
        THEN ROUND((g.target_amount - COALESCE(SUM(t.amount), 0)) / 
             NULLIF(EXTRACT(year FROM age(g.target_date, CURRENT_DATE))*12 + EXTRACT(month FROM age(g.target_date, CURRENT_DATE)), 0), 2)
        ELSE 0 
    END AS velocity_required_monthly
FROM
    ss_goals g
    LEFT JOIN ss_transactions t ON t.goal_id = g.id AND t.is_active = TRUE
GROUP BY g.id, g.name, g.target_amount, g.start_date, g.target_date;

-- 3. Canonical Goal Health View
CREATE OR REPLACE VIEW v_fact_goal_health AS
SELECT
    goal_id,
    goal_name,
    user_id,
    user_name,
    target_amount,
    actual_amount,
    completion_percent,
    CASE
        WHEN completion_percent >= 100 THEN 'achieved'
        WHEN completion_percent >= 75 THEN 'on_track'
        WHEN completion_percent >= 40 THEN 'at_risk'
        ELSE 'off_track'
    END AS goal_status
FROM
    v_fact_goal_actuals;

-- 4. Canonical Account Balance View
CREATE OR REPLACE VIEW v_fact_account_balances AS
SELECT
    user_id,
    user_name,
    bank_account_id,
    account_number,
    account_type,
    SUM(signed_amount) AS current_balance
FROM
    v_fact_transactions
GROUP BY
    user_id, user_name, bank_account_id, account_number, account_type;

-- 5. Monthly Financial Summary View
CREATE OR REPLACE VIEW v_monthly_financial_summary AS
SELECT
    DATE_TRUNC('month', transaction_date) :: date AS month,
    user_id,
    user_name,
    SUM(CASE WHEN transaction_type = 'Credit' THEN amount ELSE 0 END) AS income,
    SUM(CASE WHEN transaction_type = 'Debit' THEN amount ELSE 0 END) AS expense,
    SUM(signed_amount) AS net_cashflow
FROM
    v_fact_transactions
GROUP BY
    month, user_id, user_name;

-- 6. Rule Application Audit View
-- (Fixed: joined to ss_categorization_rules)
CREATE OR REPLACE VIEW v_rule_application_audit AS
SELECT
    t.transaction_id,
    t.transaction_date,
    t.amount,
    t.transaction_type,
    r.id AS rule_id,
    r.name AS rule_name,
    t.category_id,
    t.category_name
FROM
    v_fact_transactions t
    INNER JOIN ss_categorization_rules r ON r.id = (SELECT rule_id FROM ss_transactions WHERE id = t.transaction_id);

-- 7. Daily Cashflow Summary View
CREATE OR REPLACE VIEW v_fact_daily_cashflow AS
SELECT
    transaction_date,
    user_id,
    user_name,
    SUM(CASE WHEN transaction_type = 'Credit' THEN amount ELSE 0 END) AS daily_income,
    SUM(CASE WHEN transaction_type = 'Debit' THEN amount ELSE 0 END) AS daily_expense,
    SUM(signed_amount) AS daily_net_amount
FROM
    v_fact_transactions
GROUP BY
    transaction_date, user_id, user_name;

-- 8. Category-wise Monthly Expense View
CREATE OR REPLACE VIEW v_fact_category_monthly AS
SELECT
    DATE_TRUNC('month', transaction_date) :: date AS month,
    user_id,
    user_name,
    category_id,
    category_name,
    SUM(amount) AS total_amount
FROM
    v_fact_transactions
WHERE
    transaction_type = 'Debit'
GROUP BY
    month, user_id, user_name, category_id, category_name;

-- 9. Bank Health Summary View
CREATE OR REPLACE VIEW v_fact_bank_health AS
SELECT
    user_id,
    user_name,
    account_type,
    COUNT(DISTINCT bank_account_id) AS total_accounts,
    SUM(signed_amount) AS total_balance
FROM
    v_fact_transactions
GROUP BY
    user_id, user_name, account_type;

-- 10. Unclassified Transactions View
CREATE OR REPLACE VIEW v_fact_unclassified_transactions AS
SELECT
    transaction_id,
    transaction_date,
    user_id,
    user_name,
    account_number,
    amount,
    transaction_type,
    description
FROM
    v_fact_transactions
WHERE
    category_id IS NULL;

-- 11. Rule Coverage Summary View
CREATE OR REPLACE VIEW v_fact_rule_coverage AS
SELECT
    user_id,
    user_name,
    COUNT(*) AS total_transactions,
    COUNT(CASE WHEN transaction_id IN (SELECT id FROM ss_transactions WHERE category_id IS NOT NULL) THEN 1 END) AS rule_matched_transactions,
    COUNT(*) - COUNT(CASE WHEN transaction_id IN (SELECT id FROM ss_transactions WHERE category_id IS NOT NULL) THEN 1 END) AS unmatched_transactions,
    ROUND(
        COUNT(CASE WHEN transaction_id IN (SELECT id FROM ss_transactions WHERE category_id IS NOT NULL) THEN 1 END) :: numeric / COUNT(*) * 100,
        2
    ) AS rule_coverage_percent
FROM
    v_fact_transactions
GROUP BY
    user_id, user_name;