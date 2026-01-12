-- =============================================
-- Verification Queries
-- =============================================

-- Check data counts
SELECT 'Persons' as table_name, COUNT(*) as count FROM persons
UNION ALL
SELECT 'Goals', COUNT(*) FROM goals
UNION ALL
SELECT 'Transactions', COUNT(*) FROM transactions;

-- Summary by person
SELECT
    person,
    type,
    COUNT(*) as txn_count,
    SUM(amount) as total_amount
FROM v_transactions
GROUP BY person, type
ORDER BY person, type;

-- Monthly summary
SELECT
    year,
    month,
    month_name,
    type,
    SUM(amount) as total
FROM v_transactions
GROUP BY year, month, month_name, type
ORDER BY year, month, type;
