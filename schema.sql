-- Persons table
CREATE TABLE persons (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    relationship VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Financial goals
CREATE TABLE goals (
    id SERIAL PRIMARY KEY,
    person_id INTEGER REFERENCES persons(id),
    name VARCHAR(200) NOT NULL,  -- 'Make 1 Cr corpus'
    target_amount DECIMAL(14, 2),  -- 10000000 (1 cr)
    current_amount DECIMAL(14, 2) DEFAULT 0,
    target_percentage DECIMAL(5, 2),  -- 60
    current_percentage DECIMAL(5, 2) DEFAULT 0,  -- 35
    start_date DATE,
    target_date DATE,
    category VARCHAR(100),  -- 'Savings', 'Investment', 'Debt Payoff'
    status VARCHAR(20) DEFAULT 'Active',  -- 'Active', 'Achieved', 'Paused'
    remarks TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Transactions table (with optional goal link)
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    transaction_date DATE NOT NULL,
    person_id INTEGER REFERENCES persons(id),
    type VARCHAR(20) NOT NULL,
    category VARCHAR(100),
    entity VARCHAR(200),
    amount DECIMAL(12, 2) NOT NULL,
    purpose VARCHAR(100),
    payment_method VARCHAR(50),
    account VARCHAR(100),
    goal_id INTEGER REFERENCES goals(id),  -- Link transaction to a goal
    description TEXT,
    remarks TEXT,  -- Transaction-specific notes
    tags VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_txn_date ON transactions(transaction_date);
CREATE INDEX idx_txn_person ON transactions(person_id);
CREATE INDEX idx_txn_goal ON transactions(goal_id);
CREATE INDEX idx_goals_person ON goals(person_id);

-- View for transactions
CREATE VIEW v_transactions AS
SELECT
    t.id,
    t.transaction_date,
    p.name AS person,
    t.type,
    t.category,
    t.entity,
    t.amount,
    t.purpose,
    t.payment_method,
    t.account,
    g.name AS goal_name,
    t.description,
    t.remarks,
    t.tags,
    EXTRACT(YEAR FROM t.transaction_date) AS year,
    EXTRACT(MONTH FROM t.transaction_date) AS month,
    TO_CHAR(t.transaction_date, 'Month') AS month_name
FROM transactions t
LEFT JOIN persons p ON t.person_id = p.id
LEFT JOIN goals g ON t.goal_id = g.id;

-- View for goals with progress
CREATE VIEW v_goals AS
SELECT
    g.id,
    p.name AS person,
    g.name AS goal_name,
    g.target_amount,
    g.current_amount,
    g.target_percentage,
    g.current_percentage,
    ROUND((g.current_amount / NULLIF(g.target_amount, 0)) * 100, 2) AS amount_progress,
    g.start_date,
    g.target_date,
    g.category,
    g.status,
    g.remarks,
    COALESCE(SUM(t.amount) FILTER (WHERE t.goal_id = g.id), 0) AS total_contributions
FROM goals g
LEFT JOIN persons p ON g.person_id = p.id
LEFT JOIN transactions t ON t.goal_id = g.id
GROUP BY g.id, p.name;
