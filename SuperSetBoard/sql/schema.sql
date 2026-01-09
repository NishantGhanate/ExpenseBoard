
BEGIN;


-- Create ss_users FIRST
CREATE TABLE ss_users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    relationship VARCHAR(50),
    color VARCHAR(7),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);



CREATE TABLE ss_bank_accounts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES ss_users(id) ON DELETE CASCADE,
    number VARCHAR(20) NOT NULL,
    ifsc_code VARCHAR(11),
    type VARCHAR(11),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT uq_bank_accounts_number UNIQUE (number)
);

CREATE INDEX idx_bank_accounts_number ON ss_bank_accounts(number);
CREATE INDEX idx_bank_accounts_user_id ON ss_bank_accounts(user_id);


-- Tags -- 'sip', 'bills', 'recurring', 'one-time'
CREATE TABLE ss_tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    color VARCHAR(7),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Category -- 'Savings', 'Investment', 'Home Emi', 'Expense', etc.

-- ALTER TABLE ss_categories
-- ALTER COLUMN type TYPE category_type
-- USING type::category_type;
-- TRUNCATE TABLE ss_categories RESTART IDENTITY CASCADE;



CREATE TABLE ss_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    type VARCHAR(15),
    color VARCHAR(7),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- UPI, Wallet, Bank Transfer, Net Banking
CREATE TABLE ss_payment_methods (
    id SERIAL PRIMARY KEY,
    type VARCHAR(100) NOT NULL,
    name VARCHAR(100) NOT NULL,
    color VARCHAR(7),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Groups (for shared/family goals)
CREATE TABLE ss_groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    color VARCHAR(7),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Junction table: Group members (many-to-many)
CREATE TABLE ss_group_members (
    group_id INTEGER REFERENCES ss_groups(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES ss_users(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'member',
    joined_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (group_id, user_id)
);

-- Financial goals


CREATE TABLE ss_goals (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    target_amount DECIMAL(14, 2),
    start_date DATE,
    target_date DATE,
    status VARCHAR(10) DEFAULT 'ACTIVE',
    remarks TEXT,
    color VARCHAR(7),
    user_id INTEGER REFERENCES ss_users(id) ON DELETE CASCADE,
    group_id INTEGER REFERENCES ss_groups(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT goal_owner_check CHECK (
        (user_id IS NOT NULL AND group_id IS NULL) OR
        (user_id IS NULL AND group_id IS NOT NULL)
    ),

    CONSTRAINT valid_dates CHECK (target_date IS NULL OR target_date >= start_date),
    CONSTRAINT valid_amount CHECK (target_amount > 0)
);

CREATE INDEX idx_ss_goals_user ON ss_goals(user_id);
CREATE INDEX idx_ss_goals_status ON ss_goals(status) WHERE status = 'ACTIVE';

-- Credit, debit, internal transfer
CREATE TABLE ss_transaction_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    color VARCHAR(7),
    created_at TIMESTAMP DEFAULT NOW()
);


-- Transactions table

-- SELECT conname, pg_get_constraintdef(oid)
-- FROM pg_constraint
-- WHERE conname = 'uq_transaction_amount_reference';

CREATE TABLE ss_transactions (
    id SERIAL PRIMARY KEY,
    entity_name VARCHAR(200),
    transaction_date DATE NOT NULL,
    user_id INTEGER REFERENCES ss_users(id) NOT NULL,
    bank_account_id INTEGER REFERENCES ss_bank_accounts(id) NOT NULL,
    type_id INTEGER REFERENCES ss_transaction_types(id) NOT NULL,
    category_id INTEGER REFERENCES ss_categories(id),
    reference_id VARCHAR(100),
    tag_id INTEGER REFERENCES ss_tags(id),
    goal_id INTEGER REFERENCES ss_goals(id),
    amount DECIMAL(18, 2) NOT NULL CHECK (amount > 0),
    currency VARCHAR(3) DEFAULT 'INR',
    payment_method_id INTEGER REFERENCES ss_payment_methods(id),
    description TEXT,
    remarks TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- Unique constraint: amount + reference_id together
    CONSTRAINT uq_transaction_amount_reference UNIQUE NULLS NOT DISTINCT (amount, reference_id, bank_account_id)
);

-- Unique constraint: user_id index for faster lookups
CREATE INDEX idx_ss_transactions_user_id
    ON ss_transactions (user_id);

-- Fallback unique for transactions without reference_id
CREATE UNIQUE INDEX uq_transaction_no_reference
    ON ss_transactions (user_id, transaction_date, amount, type_id, entity_name)
    WHERE reference_id IS NULL;



-- Indexes
CREATE INDEX idx_ss_txn_date ON ss_transactions(transaction_date DESC);
CREATE INDEX idx_ss_txn_category ON ss_transactions(category_id);
CREATE INDEX idx_ss_txn_goal ON ss_transactions(goal_id) WHERE goal_id IS NOT NULL;
CREATE INDEX idx_ss_txn_type ON ss_transactions(type_id);

CREATE INDEX idx_ss_group_members_user ON ss_group_members(user_id);

COMMIT;
