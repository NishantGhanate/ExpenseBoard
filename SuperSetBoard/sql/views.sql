-- ============================================
-- VIEW 1: Full Transaction Details
-- ============================================
CREATE VIEW ss_v_transactions AS
SELECT
    t.id,
    t.transaction_date,
    t.entity_name,
    t.amount,
    t.currency,
    t.description,
    t.remarks,
    t.is_active,
    t.created_at,
    t.updated_at,

    -- Person
    p.id AS user_id,
    p.name AS person_name,
    p.color AS person_color,

    -- Type
    tt.id AS type_id,
    tt.name AS type_name,
    tt.color AS type_color,

    -- Category
    c.id AS category_id,
    c.name AS category_name,
    c.type AS category_type,
    c.color AS category_color,

    -- Tag (single)
    tg.id AS tag_id,
    tg.name AS tag_name,
    tg.color AS tag_color,

    -- Payment Method
    pm.id AS payment_method_id,
    pm.type AS payment_method_type,
    pm.name AS payment_method_name,
    pm.bank_name,
    pm.color AS payment_method_color,

    -- Goal
    g.id AS goal_id,
    g.name AS goal_name,
    g.color AS goal_color

FROM ss_transactions t
LEFT JOIN ss_users p ON t.user_id = p.id
LEFT JOIN ss_transaction_types tt ON t.type_id = tt.id
LEFT JOIN ss_categories c ON t.category_id = c.id
LEFT JOIN ss_tags tg ON t.tag_id = tg.id
LEFT JOIN ss_payment_methods pm ON t.payment_method_id = pm.id
LEFT JOIN ss_goals g ON t.goal_id = g.id;

-- Recent transactions view
CREATE VIEW ss_v_recent_transactions AS
SELECT * FROM ss_v_transactions
WHERE transaction_date >= CURRENT_DATE - INTERVAL '30 days'
  AND is_active = TRUE
ORDER BY transaction_date DESC, created_at DESC;


-- ============================================
-- VIEW 2: Goal Progress Tracking
-- ============================================
CREATE VIEW ss_v_goals AS
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

    -- Ownership type
    CASE
        WHEN g.user_id IS NOT NULL THEN 'individual'
        ELSE 'group'
    END AS ownership_type,

    -- Person (for individual goals)
    p.id AS user_id,
    p.name AS person_name,
    p.color AS person_color,

    -- Group (for group goals)
    gr.id AS group_id,
    gr.name AS group_name,
    gr.color AS group_color,

    -- Progress calculations (Debit = money going towards goal = positive contribution)
    COALESCE(SUM(t.amount), 0) AS current_amount,

    -- Progress percentage
    CASE
        WHEN g.target_amount > 0 THEN
            ROUND(COALESCE(SUM(t.amount), 0) / g.target_amount * 100, 2)
        ELSE 0
    END AS progress_percentage,

    -- Remaining amount
    GREATEST(0, g.target_amount - COALESCE(SUM(t.amount), 0)) AS remaining_amount,

    -- Transaction count
    COUNT(t.id) AS transaction_count,

    -- Total contributed
    COALESCE(SUM(t.amount), 0) AS total_contributed,

    -- Days remaining
    CASE
        WHEN g.target_date IS NOT NULL THEN
            GREATEST(0, g.target_date - CURRENT_DATE)
        ELSE NULL
    END AS days_remaining,

    -- Is goal achieved
    CASE
        WHEN COALESCE(SUM(t.amount), 0) >= g.target_amount THEN TRUE
        ELSE FALSE
    END AS is_achieved

FROM ss_goals g
LEFT JOIN ss_users p ON g.user_id = p.id
LEFT JOIN ss_groups gr ON g.group_id = gr.id
LEFT JOIN ss_transactions t ON t.goal_id = g.id AND t.is_active = TRUE
GROUP BY g.id, p.id, p.name, p.color, gr.id, gr.name, gr.color;


-- ============================================
-- VIEW 3: Group Details with Members
-- ============================================
CREATE VIEW ss_v_groups AS
SELECT
    g.id,
    g.name,
    g.description,
    g.color,
    g.is_active,
    g.created_at,
    g.updated_at,

    -- Member count
    COUNT(gm.user_id) AS member_count,

    -- Members list
    array_agg(p.name ORDER BY gm.role, p.name) AS member_names,
    array_agg(p.id ORDER BY gm.role, p.name) AS member_ids,
    array_agg(gm.role ORDER BY gm.role, p.name) AS member_roles,

    -- Goal stats for this group
    (SELECT COUNT(*) FROM ss_goals gl WHERE gl.group_id = g.id) AS total_goals,
    (SELECT COUNT(*) FROM ss_goals gl WHERE gl.group_id = g.id AND gl.status = 'active') AS active_goals

FROM ss_groups g
LEFT JOIN ss_group_members gm ON g.id = gm.group_id
LEFT JOIN ss_users p ON gm.user_id = p.id
GROUP BY g.id;


-- ============================================
-- VIEW 4: Person Summary with Stats
-- ============================================
CREATE VIEW ss_v_persons AS
SELECT
    p.id,
    p.name,
    p.email,
    p.relationship,
    p.color,
    p.is_active,
    p.created_at,

    -- Transaction stats
    COUNT(DISTINCT t.id) AS total_transactions,

    COALESCE(SUM(
        CASE WHEN tt.name IN ('credit', 'Credit') THEN t.amount ELSE 0 END
    ), 0) AS total_credits,

    COALESCE(SUM(
        CASE WHEN tt.name IN ('debit', 'Debit') THEN t.amount ELSE 0 END
    ), 0) AS total_debits,

    COALESCE(SUM(
        CASE
            WHEN tt.name IN ('credit', 'Credit') THEN t.amount
            WHEN tt.name IN ('debit', 'Debit') THEN -t.amount
            ELSE 0
        END
    ), 0) AS net_balance,

    -- Goal stats
    (SELECT COUNT(*) FROM ss_goals g WHERE g.user_id = p.id) AS individual_goals,

    -- Group memberships
    (SELECT COUNT(*) FROM ss_group_members gm WHERE gm.user_id = p.id) AS group_memberships

FROM ss_users p
LEFT JOIN ss_transactions t ON p.id = t.user_id AND t.is_active = TRUE
LEFT JOIN ss_transaction_types tt ON t.type_id = tt.id
GROUP BY p.id;


-- ============================================
-- VIEW 5: Monthly Summary
-- ============================================
CREATE VIEW ss_v_monthly_summary AS
SELECT
    DATE_TRUNC('month', t.transaction_date)::DATE AS month,
    p.id AS user_id,
    p.name AS person_name,

    -- Category breakdown
    c.id AS category_id,
    c.name AS category_name,
    c.color AS category_color,

    -- Type breakdown
    tt.name AS type_name,

    -- Aggregations
    COUNT(*) AS transaction_count,
    SUM(t.amount) AS total_amount,
    AVG(t.amount) AS avg_amount,
    MIN(t.amount) AS min_amount,
    MAX(t.amount) AS max_amount

FROM ss_transactions t
JOIN ss_users p ON t.user_id = p.id
LEFT JOIN ss_categories c ON t.category_id = c.id
LEFT JOIN ss_transaction_types tt ON t.type_id = tt.id
WHERE t.is_active = TRUE
GROUP BY DATE_TRUNC('month', t.transaction_date),
         p.id, p.name, c.id, c.name, c.color, tt.name
ORDER BY month DESC, p.name, c.name;


-- ============================================
-- VIEW 6: Category-wise Summary
-- ============================================
CREATE VIEW ss_v_category_summary AS
SELECT
    c.id AS category_id,
    c.name AS category_name,
    c.type AS category_type,
    c.color AS category_color,

    COUNT(t.id) AS transaction_count,
    COALESCE(SUM(t.amount), 0) AS total_amount,
    COALESCE(AVG(t.amount), 0) AS avg_amount,

    -- By type breakdown
    COALESCE(SUM(CASE WHEN tt.name IN ('credit', 'Credit') THEN t.amount ELSE 0 END), 0) AS credit_amount,
    COALESCE(SUM(CASE WHEN tt.name IN ('debit', 'Debit') THEN t.amount ELSE 0 END), 0) AS debit_amount,

    -- Recent activity
    MAX(t.transaction_date) AS last_transaction_date

FROM ss_categories c
LEFT JOIN ss_transactions t ON c.id = t.category_id AND t.is_active = TRUE
LEFT JOIN ss_transaction_types tt ON t.type_id = tt.id
WHERE c.is_active = TRUE
GROUP BY c.id, c.name, c.type, c.color
ORDER BY total_amount DESC;


-- ============================================
-- VIEW 7: Payment Method Summary
-- ============================================
CREATE VIEW ss_v_payment_method_summary AS
SELECT
    pm.id,
    pm.type,
    pm.name,
    pm.account_number,
    pm.bank_name,
    pm.color,
    pm.is_active,

    COUNT(t.id) AS transaction_count,
    COALESCE(SUM(t.amount), 0) AS total_amount,

    COALESCE(SUM(CASE WHEN tt.name IN ('credit', 'Credit') THEN t.amount ELSE 0 END), 0) AS total_credits,
    COALESCE(SUM(CASE WHEN tt.name IN ('debit', 'Debit') THEN t.amount ELSE 0 END), 0) AS total_debits,

    MAX(t.transaction_date) AS last_used

FROM ss_payment_methods pm
LEFT JOIN ss_transactions t ON pm.id = t.payment_method_id AND t.is_active = TRUE
LEFT JOIN ss_transaction_types tt ON t.type_id = tt.id
GROUP BY pm.id
ORDER BY transaction_count DESC;


-- ============================================
-- VIEW 8: Tag Usage Summary
-- ============================================
CREATE VIEW ss_v_tag_summary AS
SELECT
    tg.id,
    tg.name,
    tg.color,
    tg.is_active,

    COUNT(ttg.transaction_id) AS usage_count,

    COALESCE(SUM(t.amount), 0) AS total_amount,

    MAX(t.transaction_date) AS last_used

FROM ss_tags tg
LEFT JOIN ss_tags ttg ON tg.id = ttg.tag_id
LEFT JOIN ss_transactions t ON ttg.transaction_id = t.id AND t.is_active = TRUE
WHERE tg.is_active = TRUE
GROUP BY tg.id
ORDER BY usage_count DESC;


-- ============================================
-- VIEW 9: Recent Transactions (Last 30 days)
-- ============================================
CREATE VIEW ss_v_recent_transactions AS
SELECT * FROM ss_v_transactions
WHERE transaction_date >= CURRENT_DATE - INTERVAL '30 days'
  AND is_active = TRUE
ORDER BY transaction_date DESC, created_at DESC;


-- ============================================
-- VIEW 10: Active Goals Dashboard
-- ============================================
CREATE VIEW ss_v_active_goals AS
SELECT * FROM ss_v_goals
WHERE status = 'active'
ORDER BY
    CASE WHEN days_remaining IS NOT NULL THEN days_remaining ELSE 999999 END,
    progress_percentage DESC;


-- All transactions with full details
SELECT * FROM ss_v_transactions WHERE is_active = TRUE ORDER BY transaction_date DESC;

-- Goal progress
SELECT name, target_amount, current_amount, progress_percentage, days_remaining
FROM ss_v_active_goals;

-- Monthly expense breakdown
SELECT month, category_name, total_amount
FROM ss_v_monthly_summary
WHERE type_name = 'Debit'
ORDER BY month DESC, total_amount DESC;

-- Person's net balance
SELECT name, total_credits, total_debits, net_balance FROM ss_v_persons;

-- Most used payment methods
SELECT name, bank_name, transaction_count, total_amount FROM ss_v_payment_method_summary;
