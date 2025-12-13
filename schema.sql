
BEGIN;
-- Persons table
CREATE TABLE ss_persons (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    relationship VARCHAR(50),
    color VARCHAR(7),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tags -- 'sip', 'bills', 'recurring', 'one-time'
CREATE TABLE ss_tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    color VARCHAR(7),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Category -- 'Savings', 'Investment', 'Home Emi', 'Expense', etc.
CREATE TABLE ss_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    type VARCHAR(20),
    color VARCHAR(7),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- UPI, Wallet, Bank Transfer, Net Banking
CREATE TABLE ss_payment_methods (
    id SERIAL PRIMARY KEY,
    type VARCHAR(100) NOT NULL,
    name VARCHAR(100) NOT NULL,
    account_number VARCHAR(50),
    bank_name VARCHAR(100),
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
    person_id INTEGER REFERENCES ss_persons(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'member',
    joined_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (group_id, person_id)
);

-- Financial goals
CREATE TABLE ss_goals (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    target_amount DECIMAL(14, 2),
    start_date DATE,
    target_date DATE,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'achieved', 'paused', 'cancelled')),
    remarks TEXT,
    color VARCHAR(7),
    person_id INTEGER REFERENCES ss_persons(id),
    group_id INTEGER REFERENCES ss_groups(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT goal_owner_check CHECK (
        (person_id IS NOT NULL AND group_id IS NULL) OR
        (person_id IS NULL AND group_id IS NOT NULL)
    )
);

-- Credit, debit, internal transfer
CREATE TABLE ss_transaction_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    color VARCHAR(7),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Transactions table
CREATE TABLE ss_transactions (
    id SERIAL PRIMARY KEY,
    entity_name VARCHAR(200),
    transaction_date DATE NOT NULL,
    person_id INTEGER REFERENCES ss_persons(id) NOT NULL,
    type_id INTEGER REFERENCES ss_transaction_types(id) NOT NULL,
    category_id INTEGER REFERENCES ss_categories(id),
    amount DECIMAL(12, 2) NOT NULL CHECK (amount > 0),
    currency VARCHAR(3) DEFAULT 'INR',
    payment_method_id INTEGER REFERENCES ss_payment_methods(id),
    goal_id INTEGER REFERENCES ss_goals(id),
    description TEXT,
    remarks TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Junction table for multiple tags per transaction
CREATE TABLE ss_transaction_tags (
    transaction_id INTEGER REFERENCES ss_transactions(id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES ss_tags(id) ON DELETE CASCADE,
    PRIMARY KEY (transaction_id, tag_id)
);

-- Indexes
CREATE INDEX idx_ss_txn_date ON ss_transactions(transaction_date DESC);
CREATE INDEX idx_ss_txn_person ON ss_transactions(person_id);
CREATE INDEX idx_ss_txn_category ON ss_transactions(category_id);
CREATE INDEX idx_ss_txn_goal ON ss_transactions(goal_id) WHERE goal_id IS NOT NULL;
CREATE INDEX idx_ss_txn_type ON ss_transactions(type_id);
CREATE INDEX idx_ss_goals_person ON ss_goals(person_id);
CREATE INDEX idx_ss_goals_status ON ss_goals(status) WHERE status = 'active';
CREATE INDEX idx_ss_group_members_person ON ss_group_members(person_id);

COMMIT;
