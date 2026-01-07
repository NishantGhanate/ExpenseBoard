-- ============================================
-- DROP ALL ss_ TABLES
-- ============================================

BEGIN;

-- Drop views first (they depend on tables)
DROP VIEW IF EXISTS ss_v_active_goals CASCADE;
DROP VIEW IF EXISTS ss_v_recent_transactions CASCADE;
DROP VIEW IF EXISTS ss_v_tag_summary CASCADE;
DROP VIEW IF EXISTS ss_v_payment_method_summary CASCADE;
DROP VIEW IF EXISTS ss_v_category_summary CASCADE;
DROP VIEW IF EXISTS ss_v_monthly_summary CASCADE;
DROP VIEW IF EXISTS ss_v_persons CASCADE;
DROP VIEW IF EXISTS ss_v_groups CASCADE;
DROP VIEW IF EXISTS ss_v_goals CASCADE;
DROP VIEW IF EXISTS ss_v_transactions CASCADE;

-- Drop junction tables first (they have foreign keys)

DROP TABLE IF EXISTS ss_group_members CASCADE;

-- Drop tables with foreign keys
DROP TABLE IF EXISTS ss_transactions CASCADE;
DROP TABLE IF EXISTS ss_goals CASCADE;

-- Drop reference tables
DROP TABLE IF EXISTS ss_transaction_types CASCADE;
DROP TABLE IF EXISTS ss_groups CASCADE;
DROP TABLE IF EXISTS ss_payment_methods CASCADE;
DROP TABLE IF EXISTS ss_categories CASCADE;
DROP TABLE IF EXISTS ss_tags CASCADE;
DROP TABLE IF EXISTS ss_users CASCADE;
DROP TABLE IF EXISTS ss_bank_accounts CASCADE;

COMMIT;

-- Only for tx
TRUNCATE TABLE ss_transactions, ss_transaction_tags;

--- Goals
DROP VIEW IF EXISTS ss_v_goals CASCADE;
DROP VIEW IF EXISTS ss_v_active_goals CASCADE;

DROP TYPE IF EXISTS account_type_enum CASCADE;
DROP TYPE IF EXISTS goal_status_enum CASCADE;

