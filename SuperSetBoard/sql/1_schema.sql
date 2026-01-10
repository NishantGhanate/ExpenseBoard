BEGIN;

CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- 2. Set the time zone for the current database
ALTER DATABASE superset SET timezone TO 'Asia/Kolkata';

-- 1. Users Table
CREATE TABLE ss_users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    relationship VARCHAR(50),
    color VARCHAR(7),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Bank Accounts
CREATE TABLE ss_bank_accounts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES ss_users(id) ON DELETE CASCADE,
    number VARCHAR(30) NOT NULL,
    ifsc_code VARCHAR(11),
    type VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Unique per user (allows different users to have same bank/branch)
    CONSTRAINT uq_bank_accounts_user_number UNIQUE (user_id, number)
);

-- 3. Categories & Tags
CREATE TABLE ss_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    type VARCHAR(20),
    color VARCHAR(7),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE ss_tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    color VARCHAR(7),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Payment Methods & Transaction Types
CREATE TABLE ss_payment_methods (
    id SERIAL PRIMARY KEY,
    type VARCHAR(100) NOT NULL,
    name VARCHAR(100) NOT NULL,
    color VARCHAR(7),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE ss_transaction_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL, -- e.g., 'Credit', 'Debit', 'Transfer'
    is_active BOOLEAN DEFAULT TRUE,
    color VARCHAR(7),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Groups and Goals
CREATE TABLE ss_groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    color VARCHAR(7),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE ss_group_members (
    group_id INTEGER REFERENCES ss_groups(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES ss_users(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'member',
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (group_id, user_id)
);

CREATE TABLE ss_goals (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    target_amount DECIMAL(18, 2) NOT NULL,
    start_date DATE DEFAULT CURRENT_DATE,
    target_date DATE,
    status VARCHAR(20) DEFAULT 'ACTIVE',
    remarks TEXT,
    color VARCHAR(7),
    user_id INTEGER REFERENCES ss_users(id) ON DELETE CASCADE,
    group_id INTEGER REFERENCES ss_groups(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT goal_owner_check CHECK (
        (user_id IS NOT NULL AND group_id IS NULL) OR
        (user_id IS NULL AND group_id IS NOT NULL)
    ),
    CONSTRAINT valid_dates CHECK (target_date IS NULL OR target_date >= start_date),
    CONSTRAINT valid_amount CHECK (target_amount > 0)
);

-- 6. Transactions (Main Table)
CREATE TABLE ss_transactions (
    id SERIAL PRIMARY KEY,
    entity_name VARCHAR(200),
    transaction_date DATETIME NOT NULL,
    user_id INTEGER NOT NULL REFERENCES ss_users(id) ON DELETE CASCADE,
    bank_account_id INTEGER NOT NULL REFERENCES ss_bank_accounts(id) ON DELETE RESTRICT,
    type_id INTEGER NOT NULL REFERENCES ss_transaction_types(id) ON DELETE RESTRICT,
    category_id INTEGER REFERENCES ss_categories(id) ON DELETE SET NULL,
    tag_id INTEGER REFERENCES ss_tags(id) ON DELETE SET NULL,
    goal_id INTEGER REFERENCES ss_goals(id) ON DELETE SET NULL,
    payment_method_id INTEGER REFERENCES ss_payment_methods(id) ON DELETE SET NULL,

    reference_id VARCHAR(100),
    amount DECIMAL(18, 2) NOT NULL CHECK (amount > 0),
    currency VARCHAR(3) DEFAULT 'INR',
    description TEXT,
    remarks TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Prevents double-entry for same API/Bank reference
    CONSTRAINT uq_transaction_reference UNIQUE NULLS NOT DISTINCT (user_id, amount, bank_account_id, reference_id)
);

---### Optimized Indexing Strategy


-- High-speed dashboard queries (User's latest transactions)
CREATE INDEX idx_ss_txn_user_date_desc
ON ss_transactions (user_id, transaction_date DESC)
WHERE is_active = TRUE;

-- Fast reporting by category/month
CREATE INDEX idx_ss_txn_reporting
ON ss_transactions (user_id, category_id, transaction_date);

-- Optimized Foreign Key Lookups (Crucial for JOINs)
CREATE INDEX idx_ss_txn_bank_acc ON ss_transactions(bank_account_id);
CREATE INDEX idx_ss_txn_goal_id ON ss_transactions(goal_id) WHERE goal_id IS NOT NULL;

-- Unique partial index for manual entries (prevents exact accidental duplicates within 1 day)
-- Added 'description' to the mix to allow two different coffee purchases of same price
CREATE UNIQUE INDEX uq_manual_txn_prevent_dupes
ON ss_transactions (user_id, transaction_date, amount, entity_name, description)
WHERE reference_id IS NULL;

-- Search performance for entity names
CREATE INDEX idx_ss_txn_entity_name ON ss_transactions USING gin (entity_name gin_trgm_ops);
