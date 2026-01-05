BEGIN;

-- Categorization rules table
CREATE TABLE IF NOT EXISTS ss_categorization_rules (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    user_id INTEGER NOT NULL REFERENCES ss_users(id) ON DELETE CASCADE,
    bank_id INTEGER NULL,
    dsl_text TEXT NOT NULL,
    priority INTEGER DEFAULT 100,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Prevent duplicate rule names per user
    CONSTRAINT uq_rule_name_per_user UNIQUE (user_id, name)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_rule_user_id ON ss_categorization_rules(user_id);
CREATE INDEX IF NOT EXISTS idx_rules_active_priority ON ss_categorization_rules(is_active, priority);

-- Function to validate DSL on insert/update
CREATE OR REPLACE FUNCTION validate_categorization_rule()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.dsl_text IS NULL OR LENGTH(TRIM(NEW.dsl_text)) = 0 THEN
        RAISE EXCEPTION 'DSL text cannot be empty';
    END IF;

    NEW.updated_at = NOW();  -- Auto-update timestamp
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for validation
DROP TRIGGER IF EXISTS validate_rule_trigger ON ss_categorization_rules;
CREATE TRIGGER validate_rule_trigger
    BEFORE INSERT OR UPDATE ON ss_categorization_rules
    FOR EACH ROW EXECUTE FUNCTION validate_categorization_rule();

COMMIT;
