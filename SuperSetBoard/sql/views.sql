BEGIN;

-- ============================================
-- VIEW 1: Full Transaction Details
-- ============================================
CREATE OR REPLACE VIEW ss_v_transactions AS
SELECT
    t.id,
    t.transaction_date,
    t.entity_name,
    t.amount,
    t.currency,
    t.description,
    t.remarks,
    t.is_active,
    t.reference_id,
    t.created_at,
    t.updated_at,

    -- User
    u.id AS user_id,
    u.name AS user_name,
    u.color AS user_color,

    -- Bank Account
    ba.id AS bank_account_id,
    ba.number AS bank_account_number,
    ba.type AS bank_account_type,

    -- Type
    tt.id AS type_id,
    tt.name AS type_name,
    tt.color AS type_color,

    -- Category
    c.id AS category_id,
    c.name AS category_name,
    c.type AS category_type,
    c.color AS category_color,

    -- Tag
    tg.id AS tag_id,
    tg.name AS tag_name,
    tg.color AS tag_color,

    -- Payment Method
    pm.id AS payment_method_id,
    pm.name AS payment_method_name,
    pm.color AS payment_method_color,

    -- Goal
    g.id AS goal_id,
    g.name AS goal_name

FROM ss_transactions t
LEFT JOIN ss_users u ON t.user_id = u.id
LEFT JOIN ss_bank_accounts ba ON t.bank_account_id = ba.id
LEFT JOIN ss_transaction_types tt ON t.type_id = tt.id
LEFT JOIN ss_categories c ON t.category_id = c.id
LEFT JOIN ss_tags tg ON t.tag_id = tg.id
LEFT JOIN ss_payment_methods pm ON t.payment_method_id = pm.id
LEFT JOIN ss_goals g ON t.goal_id = g.id;


-- ============================================
-- VIEW 2: Goal Progress Tracking
-- ============================================
CREATE OR REPLACE VIEW ss_v_goals AS
SELECT
    g.id,
    g.name,
    g.target_amount,
    g.start_date,
    g.target_date,
    g.status,
    g.remarks,
    g.color,
    g.created_at,
    g.updated_at,

    CASE WHEN g.user_id IS NOT NULL THEN 'individual' ELSE 'group' END AS ownership_type,

    u.name AS owner_name,
    gr.name AS group_name,

    COALESCE(SUM(t.amount), 0) AS current_amount,
    CASE
        WHEN g.target_amount > 0 THEN ROUND(COALESCE(SUM(t.amount), 0) / g.target_amount * 100, 2)
        ELSE 0
    END AS progress_percentage,
    GREATEST(0, g.target_amount - COALESCE(SUM(t.amount), 0)) AS remaining_amount,
    COUNT(t.id) AS transaction_count,
    CASE
        WHEN g.target_date IS NOT NULL THEN GREATEST(0, g.target_date - CURRENT_DATE)
        ELSE NULL
    END AS days_remaining,
    (COALESCE(SUM(t.amount), 0) >= g.target_amount) AS is_achieved

FROM ss_goals g
LEFT JOIN ss_users u ON g.user_id = u.id
LEFT JOIN ss_groups gr ON g.group_id = gr.id
LEFT JOIN ss_transactions t ON t.goal_id = g.id AND t.is_active = TRUE
GROUP BY g.id, u.name, gr.name;


-- ============================================
-- VIEW 3: Group Details with Members
-- ============================================
CREATE OR REPLACE VIEW ss_v_groups AS
SELECT
    g.id,
    g.name,
    g.description,
    g.color,
    g.is_active,
    g.created_at,

    COUNT(gm.user_id) AS member_count,
    array_agg(u.name ORDER BY gm.role) AS member_names,
    (SELECT COUNT(*) FROM ss_goals gl WHERE gl.group_id = g.id) AS total_goals,
    (SELECT COUNT(*) FROM ss_goals gl WHERE gl.group_id = g.id AND gl.status ILIKE 'ACTIVE%') AS active_goals

FROM ss_groups g
LEFT JOIN ss_group_members gm ON g.id = gm.group_id
LEFT JOIN ss_users u ON gm.user_id = u.id
GROUP BY g.id;


-- ============================================
-- VIEW 4: User/Person Summary
-- ============================================
CREATE OR REPLACE VIEW ss_v_persons AS
SELECT
    u.id,
    u.name,
    u.email,
    u.relationship,
    u.is_active,

    COUNT(DISTINCT t.id) AS total_transactions,
    COALESCE(SUM(CASE WHEN tt.name ILIKE 'Credit%' THEN t.amount ELSE 0 END), 0) AS total_credits,
    COALESCE(SUM(CASE WHEN tt.name ILIKE 'Debit%' THEN t.amount ELSE 0 END), 0) AS total_debits,
    COALESCE(SUM(CASE WHEN tt.name ILIKE 'Credit%' THEN t.amount ELSE -t.amount END), 0) AS net_balance

FROM ss_users u
LEFT JOIN ss_transactions t ON u.id = t.user_id AND t.is_active = TRUE
LEFT JOIN ss_transaction_types tt ON t.type_id = tt.id
GROUP BY u.id;


-- ============================================
-- VIEW 5: Monthly Summary (The Breakdown)
-- ============================================
CREATE OR REPLACE VIEW ss_v_monthly_summary AS
SELECT
    DATE_TRUNC('month', t.transaction_date)::DATE AS month,
    t.user_id,
    u.name AS user_name,
    c.name AS category_name,
    tt.name AS type_name,
    SUM(t.amount) AS total_amount,
    COUNT(*) AS transaction_count
FROM ss_transactions t
JOIN ss_users u ON t.user_id = u.id
LEFT JOIN ss_categories c ON t.category_id = c.id
LEFT JOIN ss_transaction_types tt ON t.type_id = tt.id
WHERE t.is_active = TRUE
GROUP BY
    DATE_TRUNC('month', t.transaction_date),
    t.user_id,
    u.name,
    c.name,
    tt.name;


-- ============================================
-- VIEW 6: Category-wise Summary
-- ============================================
CREATE OR REPLACE VIEW ss_v_category_summary AS
SELECT
    c.id,
    c.name,
    c.type AS category_type,
    COUNT(t.id) AS usage_count,
    COALESCE(SUM(t.amount), 0) AS total_amount,
    MAX(t.transaction_date) AS last_used
FROM ss_categories c
LEFT JOIN ss_transactions t ON c.id = t.category_id AND t.is_active = TRUE
WHERE c.is_active = TRUE
GROUP BY c.id;


-- ============================================
-- VIEW 7: Bank Account Summary (Replaces old PM View)
-- ============================================
CREATE OR REPLACE VIEW ss_v_bank_summary AS
SELECT
    ba.id,
    ba.number,
    ba.type,
    u.name AS owner_name,
    COUNT(t.id) AS txn_count,
    COALESCE(SUM(CASE WHEN tt.name ILIKE 'Credit%' THEN t.amount ELSE -t.amount END), 0) AS current_ledger_balance
FROM ss_bank_accounts ba
JOIN ss_users u ON ba.user_id = u.id
LEFT JOIN ss_transactions t ON ba.id = t.bank_account_id AND t.is_active = TRUE
LEFT JOIN ss_transaction_types tt ON t.type_id = tt.id
GROUP BY ba.id, u.name;


-- ============================================
-- VIEW 8: Tag Usage Summary
-- ============================================
CREATE OR REPLACE VIEW ss_v_tag_summary AS
SELECT
    tg.id,
    tg.name,
    COUNT(t.id) AS usage_count,
    SUM(t.amount) AS total_volume
FROM ss_tags tg
LEFT JOIN ss_transactions t ON tg.id = t.tag_id AND t.is_active = TRUE
GROUP BY tg.id;


-- ============================================
-- VIEW 9: Recent Transactions (30 Days)
-- ============================================
CREATE OR REPLACE VIEW ss_v_recent_transactions AS
SELECT * FROM ss_v_transactions
WHERE transaction_date >= CURRENT_DATE - INTERVAL '30 days'
  AND is_active = TRUE;


-- ============================================
-- VIEW 10: Active Goals Dashboard
-- ============================================
CREATE OR REPLACE VIEW ss_v_active_goals AS
SELECT * FROM ss_v_goals
WHERE status ILIKE 'ACTIVE%'
ORDER BY days_remaining ASC;

COMMIT;
