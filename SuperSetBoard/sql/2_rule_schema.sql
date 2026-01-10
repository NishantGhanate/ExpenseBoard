BEGIN;

-- 1. Categorization rules table
CREATE TABLE IF NOT EXISTS ss_categorization_rules (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(255), -- Added to explain what the rule does
    user_id INTEGER NOT NULL REFERENCES ss_users(id) ON DELETE CASCADE,
    bank_account_id INTEGER REFERENCES ss_bank_accounts(id) ON DELETE CASCADE,

    -- The core logic
    dsl_text TEXT NOT NULL,
    -- Optional: If you want to store the result of the rule (e.g. category_id to apply)
    target_category_id INTEGER REFERENCES ss_categories(id) ON DELETE SET NULL,

    priority INTEGER DEFAULT 100, -- Lower numbers run first
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Prevent duplicate rule names per user
    CONSTRAINT uq_rule_name_per_user UNIQUE (user_id, name)
);

-- 2. Refined Indexes
CREATE INDEX IF NOT EXISTS idx_rule_user_priority
    ON ss_categorization_rules(user_id, priority)
    WHERE is_active = TRUE;

-- 3. Validation and Timestamp Function
CREATE OR REPLACE FUNCTION fn_ss_categorization_rules_sync()
RETURNS TRIGGER AS $$
BEGIN
    -- Validation logic
    IF NEW.dsl_text IS NULL OR LENGTH(TRIM(NEW.dsl_text)) = 0 THEN
        RAISE EXCEPTION 'DSL text cannot be empty';
    END IF;

    -- Update the timestamp
    NEW.updated_at = NOW();

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 4. Trigger
DROP TRIGGER IF EXISTS trg_ss_categorization_rules_sync ON ss_categorization_rules;
CREATE TRIGGER trg_ss_categorization_rules_sync
    BEFORE INSERT OR UPDATE ON ss_categorization_rules
    FOR EACH ROW EXECUTE FUNCTION fn_ss_categorization_rules_sync();

COMMIT;
