-- ============================================
-- SEED DATA FOR EXPENSE BOARD
-- ============================================

BEGIN;
-- ============================================
-- 1.  USERS (2 users)
-- ============================================
INSERT INTO ss_users (name, email, relationship, color, is_active) VALUES
('Nishant', 'nishant7.ng@example.com', 'self', '#3B82F6', TRUE),
('Rinisha', 'rburriwar196@gmail.com', 'self', '#3B82F6', TRUE),

-- ============================================
-- 2. TAGS (SUB BIN)
-- ============================================
INSERT INTO ss_tags (name, is_active, color) VALUES
('sip', TRUE, '#10B981'),
('gold', TRUE, '#10B981'),
('bills', TRUE, '#F59E0B'),
('recurring', TRUE, '#6366F1'),
('one-time', TRUE, '#8B5CF6'),
('essential', TRUE, '#EF4444'),
('discretionary', TRUE, '#14B8A6');

-- ============================================
-- 3. CATEGORIES (BINS)
-- Truncate table ss_categories RESTART IDENTITY CASCADE;
-- ============================================

INSERT INTO ss_categories (name, type, color, is_active) VALUES
('Salary', 'INCOME', '#22C55E', TRUE),
('Freelance', 'INCOME', '#14B8A6', TRUE),
('Investment', 'INCOME', '#3B82F6', TRUE),
('Term Insurance', 'EXPENSE', '#F97316', TRUE),
('Sbi Home Emi', 'EXPENSE', '#EF4444', TRUE),
('Utilities', 'EXPENSE', '#F59E0B', TRUE),
('Groceries', 'EXPENSE', '#84CC16', TRUE),
('Entertainment', 'EXPENSE', '#A855F7', TRUE),
('Healthcare', 'EXPENSE', '#EC4899', TRUE),
('Transfer', 'INCOME', '#6B7280', TRUE),
('Health Insurance', 'EXPENSE', '#F97316', TRUE)
ON CONFLICT (name) DO UPDATE SET
    type = EXCLUDED.type,
    color = EXCLUDED.color,
    is_active = EXCLUDED.is_active;

-- ============================================
-- 4. PAYMENT METHODS

-- select * from ss_payment_methods

-- TRUNCATE TABLE ss_payment_methods RESTART IDENTITY CASCADE;

-- ============================================
INSERT INTO ss_payment_methods (type, name, color, is_active) VALUES
('UPI', 'Kotak UPI', '#FF0000', TRUE),
('UPI', 'HDFC UPI', '#004C8F', TRUE),
('Net Banking', 'Kotak Net Banking', '#FF0000', TRUE),
('Net Banking', 'HDFC Net Banking', '#004C8F', TRUE),
('Wallet', 'PhonePe', '#00BAF2', TRUE),
('UPI', 'PhonePe', '#00BAF2', TRUE),
('Bank Transfer', 'NEFT/IMPS', '#FF0000', TRUE),
('RTNCHG', 'Auto Debit', '#FF0000', TRUE),
('NACH', 'Auto clearing', '#FF0000', TRUE),
('NEFT', 'Bank Transfer', '#FF0000', TRUE);


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
('Mini', 'Couple finance', '#8B5CF6', TRUE);

-- ============================================
-- 7. GROUP MEMBERS
-- ============================================
INSERT INTO ss_group_members (group_id, user_id, role) VALUES
(1, 1, 'owner'),
(1, 2, 'member');

-- ============================================
-- 8. GOALS
-- ============================================
INSERT INTO ss_goals (name, target_amount, start_date, target_date, status, remarks, color, user_id, group_id) VALUES
('SIP Fund', 10000000.00, '2026-01-01', '2036-01-01', 'ACTIVE', 'Core', '#F59E0B', 1, NULL);
('Emergency Fund', 1000000.00, '2024-01-01', '2027-12-30', 'ACTIVE', '6 months expenses', '#22C55E', 1, NULL),
('House Down Payment', 2000000.00, '2024-01-01', '2030-12-31', 'ACTIVE', 'For new house', '#3B82F6', NULL, 1),
('Vacation Fund', 200000.00, '2024-06-01', '2026-30-01', 'ACTIVE', 'Europe trip', '#F59E0B', 2, NULL),



-- ============================================
-- 9. TRANSACTIONS (24 records per user = 48 total)
-- ============================================


COMMIT;
