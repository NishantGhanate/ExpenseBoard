-- ============================================
-- SEED DATA FOR EXPENSE BOARD
-- ============================================

BEGIN;
-- ============================================
-- 1. PERSONS (2 users)
-- ============================================
INSERT INTO ss_persons (name, email, relationship, color, is_active) VALUES
('Nishant', 'nishant@example.com', 'self', '#3B82F6', TRUE),
('Mini', 'Mini@example.com', 'spouse', '#EC4899', TRUE);

-- ============================================
-- 2. TAGS
-- ============================================
INSERT INTO ss_tags (name, is_active, color) VALUES
('sip', TRUE, '#10B981'),
('bills', TRUE, '#F59E0B'),
('recurring', TRUE, '#6366F1'),
('one-time', TRUE, '#8B5CF6'),
('essential', TRUE, '#EF4444'),
('discretionary', TRUE, '#14B8A6');

-- ============================================
-- 3. CATEGORIES
-- ============================================
INSERT INTO ss_categories (name, type, color, is_active) VALUES
('Salary', 'income', '#22C55E', TRUE),
('Investment', 'investment', '#3B82F6', TRUE),
('Home EMI', 'expense', '#EF4444', TRUE),
('Utilities', 'expense', '#F59E0B', TRUE),
('Groceries', 'expense', '#84CC16', TRUE),
('Entertainment', 'expense', '#A855F7', TRUE),
('Healthcare', 'expense', '#EC4899', TRUE),
('Transfer', 'transfer', '#6B7280', TRUE),
('Freelance', 'income', '#14B8A6', TRUE),
('Term Insurance', 'expense', '#F97316', TRUE),
('Health Insurance', 'expense', '#F97316', TRUE);

-- ============================================
-- 4. PAYMENT METHODS
-- ============================================
INSERT INTO ss_payment_methods (type, name, account_number, bank_name, color, is_active) VALUES
('UPI', 'Kotak UPI', 'XXXX1234', 'Kotak Mahindra Bank', '#FF0000', TRUE),
('UPI', 'HDFC UPI', 'XXXX5678', 'HDFC Bank', '#004C8F', TRUE),
('Net Banking', 'Kotak Net Banking', 'XXXX1234', 'Kotak Mahindra Bank', '#FF0000', TRUE),
('Net Banking', 'HDFC Net Banking', 'XXXX5678', 'HDFC Bank', '#004C8F', TRUE),
('Wallet', 'PhonePe', NULL, NULL, '#00BAF2', TRUE),
('Bank Transfer', 'NEFT/IMPS', 'XXXX1234', 'Kotak Mahindra Bank', '#FF0000', TRUE);

-- ============================================
-- 5. TRANSACTION TYPES
-- ============================================
INSERT INTO ss_transaction_types (name, is_active, color) VALUES
('Credit', TRUE, '#22C55E'),
('Debit', TRUE, '#EF4444'),
('Transfer', TRUE, '#6B7280');

-- ============================================
-- 6. GROUPS
-- ============================================
INSERT INTO ss_groups (name, description, color, is_active) VALUES
('Family', 'Joint family finances', '#8B5CF6', TRUE);

-- ============================================
-- 7. GROUP MEMBERS
-- ============================================
INSERT INTO ss_group_members (group_id, person_id, role) VALUES
(1, 1, 'owner'),
(1, 2, 'member');

-- ============================================
-- 8. GOALS
-- ============================================
INSERT INTO ss_goals (name, target_amount, start_date, target_date, status, remarks, color, person_id, group_id) VALUES
('Emergency Fund', 500000.00, '2024-01-01', '2025-12-31', 'active', '6 months expenses', '#22C55E', 1, NULL),
('House Down Payment', 2000000.00, '2024-01-01', '2026-12-31', 'active', 'For new house', '#3B82F6', NULL, 1),
('Vacation Fund', 200000.00, '2024-06-01', '2025-06-01', 'active', 'Europe trip', '#F59E0B', 2, NULL);

-- ============================================
-- 9. TRANSACTIONS (24 records per user = 48 total)
-- Monthly from Jan 2024 to Dec 2025
-- ============================================

-- NISHANT's Transactions (person_id = 1)
INSERT INTO ss_transactions (entity_name, transaction_date, person_id, type_id, category_id, amount, currency, payment_method_id, goal_id, description, remarks, is_active) VALUES
-- 2024
('TechCorp India', '2024-01-05', 1, 1, 1, 150000.00, 'INR', 4, NULL, 'January Salary', 'Monthly salary', TRUE),
('HDFC MF', '2024-01-10', 1, 2, 2, 25000.00, 'INR', 4, 1, 'SIP Investment', 'Monthly SIP', TRUE),
('TechCorp India', '2024-02-05', 1, 1, 1, 150000.00, 'INR', 4, NULL, 'February Salary', 'Monthly salary', TRUE),
('ICICI Prudential', '2024-02-15', 1, 2, 10, 45000.00, 'INR', 3, NULL, 'Term Insurance Premium', 'Annual premium', TRUE),
('TechCorp India', '2024-03-05', 1, 1, 1, 150000.00, 'INR', 4, NULL, 'March Salary', 'Monthly salary', TRUE),
('HDFC Bank', '2024-03-10', 1, 2, 3, 35000.00, 'INR', 6, NULL, 'Home EMI', 'Monthly EMI', TRUE),
('TechCorp India', '2024-04-05', 1, 1, 1, 150000.00, 'INR', 4, NULL, 'April Salary', 'Monthly salary', TRUE),
('Zerodha', '2024-04-20', 1, 2, 2, 50000.00, 'INR', 4, 2, 'Mutual Fund Lumpsum', 'Additional investment', TRUE),
('TechCorp India', '2024-05-05', 1, 1, 1, 155000.00, 'INR', 4, NULL, 'May Salary', 'Salary with increment', TRUE),
('Apollo Hospital', '2024-05-18', 1, 2, 7, 12000.00, 'INR', 1, NULL, 'Health Checkup', 'Annual checkup', TRUE),
('TechCorp India', '2024-06-05', 1, 1, 1, 155000.00, 'INR', 4, NULL, 'June Salary', 'Monthly salary', TRUE),
('BigBasket', '2024-06-12', 1, 2, 5, 8500.00, 'INR', 1, NULL, 'Monthly Groceries', 'June groceries', TRUE),
('TechCorp India', '2024-07-05', 1, 1, 1, 155000.00, 'INR', 4, NULL, 'July Salary', 'Monthly salary', TRUE),
('Netflix', '2024-07-01', 1, 2, 6, 649.00, 'INR', 5, NULL, 'Netflix Subscription', 'Monthly subscription', TRUE),
('TechCorp India', '2024-08-05', 1, 1, 1, 155000.00, 'INR', 4, NULL, 'August Salary', 'Monthly salary', TRUE),
('Tata Power', '2024-08-10', 1, 2, 4, 3200.00, 'INR', 1, NULL, 'Electricity Bill', 'August bill', TRUE),
('TechCorp India', '2024-09-05', 1, 1, 1, 155000.00, 'INR', 4, NULL, 'September Salary', 'Monthly salary', TRUE),
('HDFC MF', '2024-09-10', 1, 2, 2, 25000.00, 'INR', 4, 1, 'SIP Investment', 'Monthly SIP', TRUE),
('TechCorp India', '2024-10-05', 1, 1, 1, 155000.00, 'INR', 4, NULL, 'October Salary', 'Monthly salary', TRUE),
('Income Tax Dept', '2024-10-15', 1, 2, 2, 75000.00, 'INR', 3, NULL, 'Advance Tax Q2', 'Quarterly advance tax', TRUE),
('TechCorp India', '2024-11-05', 1, 1, 1, 155000.00, 'INR', 4, NULL, 'November Salary', 'Monthly salary', TRUE),
('Amazon', '2024-11-25', 1, 2, 6, 15000.00, 'INR', 2, NULL, 'Diwali Shopping', 'Festival shopping', TRUE),
('TechCorp India', '2024-12-05', 1, 1, 1, 155000.00, 'INR', 4, NULL, 'December Salary', 'Monthly salary', TRUE),
('HDFC Bank', '2024-12-10', 1, 2, 3, 35000.00, 'INR', 6, NULL, 'Home EMI', 'Monthly EMI', TRUE),

-- mini's Transactions (person_id = 2)
-- 2024
('DesignStudio', '2024-01-07', 2, 1, 1, 85000.00, 'INR', 2, NULL, 'January Salary', 'Monthly salary', TRUE),
('DMart', '2024-01-15', 2, 2, 5, 6500.00, 'INR', 1, NULL, 'Groceries', 'Monthly groceries', TRUE),
('DesignStudio', '2024-02-07', 2, 1, 1, 85000.00, 'INR', 2, NULL, 'February Salary', 'Monthly salary', TRUE),
('Jio', '2024-02-10', 2, 2, 4, 999.00, 'INR', 5, NULL, 'Mobile Recharge', 'Quarterly recharge', TRUE),
('DesignStudio', '2024-03-07', 2, 1, 1, 85000.00, 'INR', 2, NULL, 'March Salary', 'Monthly salary', TRUE),
('SBI MF', '2024-03-15', 2, 2, 2, 15000.00, 'INR', 4, 3, 'SIP Investment', 'Vacation fund SIP', TRUE),
('DesignStudio', '2024-04-07', 2, 1, 1, 85000.00, 'INR', 2, NULL, 'April Salary', 'Monthly salary', TRUE),
('Myntra', '2024-04-12', 2, 2, 6, 8500.00, 'INR', 1, NULL, 'Summer Shopping', 'Clothes shopping', TRUE),
('DesignStudio', '2024-05-07', 2, 1, 1, 90000.00, 'INR', 2, NULL, 'May Salary', 'Salary with bonus', TRUE),
('Star Health', '2024-05-20', 2, 2, 10, 22000.00, 'INR', 4, NULL, 'Health Insurance', 'Annual premium', TRUE),
('DesignStudio', '2024-06-07', 2, 1, 1, 85000.00, 'INR', 2, NULL, 'June Salary', 'Monthly salary', TRUE),
('PVR Cinemas', '2024-06-22', 2, 2, 6, 1200.00, 'INR', 5, NULL, 'Movie Night', 'Weekend movie', TRUE),
('DesignStudio', '2024-07-07', 2, 1, 1, 85000.00, 'INR', 2, NULL, 'July Salary', 'Monthly salary', TRUE),
('Mahanagar Gas', '2024-07-15', 2, 2, 4, 1800.00, 'INR', 1, NULL, 'Gas Bill', 'Monthly gas', TRUE),
('DesignStudio', '2024-08-07', 2, 1, 1, 85000.00, 'INR', 2, NULL, 'August Salary', 'Monthly salary', TRUE),
('Cult.fit', '2024-08-01', 2, 2, 7, 2500.00, 'INR', 1, NULL, 'Gym Membership', 'Monthly membership', TRUE),
('DesignStudio', '2024-09-07', 2, 1, 1, 85000.00, 'INR', 2, NULL, 'September Salary', 'Monthly salary', TRUE),
('SBI MF', '2024-09-15', 2, 2, 2, 15000.00, 'INR', 4, 3, 'SIP Investment', 'Vacation fund SIP', TRUE),
('DesignStudio', '2024-10-07', 2, 1, 1, 85000.00, 'INR', 2, NULL, 'October Salary', 'Monthly salary', TRUE),
('Tanishq', '2024-10-28', 2, 2, 6, 45000.00, 'INR', 2, NULL, 'Diwali Jewelry', 'Festival purchase', TRUE),
('DesignStudio', '2024-11-07', 2, 1, 1, 85000.00, 'INR', 2, NULL, 'November Salary', 'Monthly salary', TRUE),
('Swiggy', '2024-11-15', 2, 2, 5, 3500.00, 'INR', 5, NULL, 'Food Delivery', 'Monthly food orders', TRUE),
('DesignStudio', '2024-12-07', 2, 1, 1, 170000.00, 'INR', 2, NULL, 'December Salary + Bonus', 'Year end bonus', TRUE),
('MakeMyTrip', '2024-12-20', 2, 2, 6, 35000.00, 'INR', 2, 3, 'Goa Trip Booking', 'New year vacation', TRUE);

-- ============================================
-- 10. TRANSACTION TAGS (Link tags to transactions)
-- ============================================
INSERT INTO ss_transaction_tags (transaction_id, tag_id) VALUES
-- Nishant's tags
(2, 1),   -- SIP
(2, 3),   -- recurring
(4, 5),   -- essential (insurance)
(6, 3),   -- recurring (EMI)
(6, 5),   -- essential
(8, 4),   -- one-time
(10, 5),  -- essential (health)
(12, 3),  -- recurring (groceries)
(14, 3),  -- recurring (subscription)
(16, 2),  -- bills
(18, 1),  -- SIP
(18, 3),  -- recurring
(22, 4),  -- one-time (shopping)
(24, 3),  -- recurring (EMI)

-- Mini's tags
(26, 3),  -- recurring (groceries)
(28, 2),  -- bills
(30, 1),  -- SIP
(30, 3),  -- recurring
(32, 6),  -- discretionary
(34, 5),  -- essential (insurance)
(36, 6),  -- discretionary
(38, 2),  -- bills
(40, 3),  -- recurring (gym)
(42, 1),  -- SIP
(42, 3),  -- recurring
(44, 4),  -- one-time
(46, 6),  -- discretionary
(48, 4);  -- one-time (vacation)

COMMIT;
