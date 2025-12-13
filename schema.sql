-- Persons table
CREATE TABLE persons (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    user_email VARCHAR(100),  -- Increased length for emails
    relationship VARCHAR(50),
    color VARCHAR(7),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tags -- 'sip', 'bills', 'recurring', 'one-time'
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    color VARCHAR(7),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Category -- 'Savings', 'Investment', 'Home Emi', 'Expense', etc.
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    type VARCHAR(20),
    color VARCHAR(7),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- UPI, Wallet, Bank Transfer, Net Banking
CREATE TABLE payment_methods (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    account_number VARCHAR(50),
    bank_name VARCHAR(100),
    color VARCHAR(7),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Groups (for shared/family goals)
CREATE TABLE groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    color VARCHAR(7),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Junction table: Group members (many-to-many)
CREATE TABLE group_members (
    group_id INTEGER REFERENCES groups(id) ON DELETE CASCADE,
    person_id INTEGER REFERENCES persons(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'member',
    joined_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (group_id, person_id)
);

-- Financial goals
CREATE TABLE goals (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    target_amount DECIMAL(14, 2),
    start_date DATE,
    target_date DATE,
    category_id INTEGER REFERENCES categories(id),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'achieved', 'paused', 'cancelled')),
    remarks TEXT,
    color VARCHAR(7),
    person_id INTEGER REFERENCES persons(id),
    group_id INTEGER REFERENCES groups(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT goal_owner_check CHECK (
        (person_id IS NOT NULL AND group_id IS NULL) OR
        (person_id IS NULL AND group_id IS NOT NULL)
    )
);

-- Credit, debit, internal transfer
CREATE TABLE transaction_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    color VARCHAR(7),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Transactions table
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    entity_name VARCHAR(200),  -- Fixed: removed space, made optional
    transaction_date DATE NOT NULL,
    person_id INTEGER REFERENCES persons(id) NOT NULL,
    type_id INTEGER REFERENCES transaction_types(id) NOT NULL,
    category_id INTEGER REFERENCES categories(id),
    amount DECIMAL(12, 2) NOT NULL CHECK (amount > 0),
    currency VARCHAR(3) DEFAULT 'INR',
    purpose VARCHAR(100),
    payment_method_id INTEGER REFERENCES payment_methods(id),
    goal_id INTEGER REFERENCES goals(id),
    description TEXT,
    remarks TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Junction table for multiple tags per transaction
CREATE TABLE transaction_tags (
    transaction_id INTEGER REFERENCES transactions(id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (transaction_id, tag_id)
);

-- Indexes
CREATE INDEX idx_txn_date ON transactions(transaction_date DESC);
CREATE INDEX idx_txn_person ON transactions(person_id);
CREATE INDEX idx_txn_category ON transactions(category_id);
CREATE INDEX idx_txn_goal ON transactions(goal_id) WHERE goal_id IS NOT NULL;
CREATE INDEX idx_txn_type ON transactions(type_id);
CREATE INDEX idx_goals_person ON goals(person_id);
CREATE INDEX idx_goals_status ON goals(status) WHERE status = 'active';
CREATE INDEX idx_group_members_person ON group_members(person_id);
