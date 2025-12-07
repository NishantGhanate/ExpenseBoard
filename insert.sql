-- =============================================
-- Sample Data: Persons
-- =============================================

INSERT INTO persons (name, relationship) VALUES
    ('Nishant', 'Self'),
    ('Minisha', 'Spouse'),
    ('Mini', 'Bot');

-- =============================================
-- Sample Data: Goals
-- =============================================

INSERT INTO goals (person_id, name, target_amount, current_amount, target_percentage, current_percentage, start_date, target_date, category, status, remarks) VALUES
    (1, '1 Crore Corpus', 10000000, 3500000, 100, 35, '2023-01-01', '2030-12-31', 'Retirement', 'Active', 'Long term retirement fund'),
    (1, 'Emergency Fund', 500000, 350000, 100, 70, '2024-01-01', '2024-12-31', 'Savings', 'Active', '6 months expenses'),
    (1, 'Car Down Payment', 300000, 180000, 100, 60, '2024-06-01', '2025-06-30', 'Purchase', 'Active', 'New car fund'),
    (2, 'Vacation Fund', 200000, 80000, 100, 40, '2024-01-01', '2024-12-31', 'Leisure', 'Active', 'Europe trip'),
    (1, 'Home Loan Prepayment', 1000000, 250000, 100, 25, '2024-01-01', '2026-12-31', 'Debt', 'Active', 'Reduce loan tenure');

-- =============================================
-- Sample Data: Transactions (Oct-Dec 2024)
-- =============================================

-- October 2024
INSERT INTO transactions (transaction_date, person_id, type, category, entity, amount, purpose, payment_method, account, goal_id, description, remarks, tags) VALUES
-- Salary Credits
('2024-10-01', 1, 'Credit', 'Salary', 'TechCorp India', 185000, 'Income', 'Bank Transfer', 'HDFC Salary', NULL, 'October salary', NULL, 'salary,income'),
('2024-10-05', 2, 'Credit', 'Salary', 'InfoSys Ltd', 95000, 'Income', 'Bank Transfer', 'ICICI Salary', NULL, 'October salary', NULL, 'salary,income'),

-- Investments
('2024-10-02', 1, 'Debit', 'Investment', 'Zerodha', 25000, 'Investment', 'Auto Debit', 'HDFC Salary', 1, 'SIP - Nifty 50 Index', 'Monthly SIP', 'sip,mutual-fund'),
('2024-10-02', 1, 'Debit', 'Investment', 'Zerodha', 15000, 'Investment', 'Auto Debit', 'HDFC Salary', 1, 'SIP - Midcap Fund', 'Monthly SIP', 'sip,mutual-fund'),
('2024-10-05', 1, 'Debit', 'Investment', 'Kuvera', 10000, 'Investment', 'Auto Debit', 'ICICI Salary', 2, 'Liquid Fund - Emergency', NULL, 'liquid-fund,emergency'),

-- EMIs
('2024-10-05', 1, 'Debit', 'EMI', 'HDFC Home Loan', 42000, 'Expense', 'Auto Debit', 'HDFC Salary', NULL, 'Home loan EMI', NULL, 'emi,home-loan'),
('2024-10-10', 2, 'Debit', 'EMI', 'Bajaj Finance', 8500, 'Expense', 'Auto Debit', 'ICICI Salary', NULL, 'iPhone EMI', NULL, 'emi,phone'),

-- Utilities
('2024-10-08', 1, 'Debit', 'Bills & Utilities', 'Adani Electricity', 3200, 'Expense', 'Auto Debit', 'HDFC Salary', NULL, 'Electricity bill', NULL, 'bills,electricity'),
('2024-10-10', 1, 'Debit', 'Bills & Utilities', 'Mahanagar Gas', 1800, 'Expense', 'UPI', 'HDFC Salary', NULL, 'Gas bill', NULL, 'bills,gas'),
('2024-10-12', 1, 'Debit', 'Bills & Utilities', 'Jio Fiber', 1499, 'Expense', 'Auto Debit', 'HDFC Salary', NULL, 'Internet + TV', NULL, 'bills,internet'),
('2024-10-12', 1, 'Debit', 'Bills & Utilities', 'Airtel', 599, 'Expense', 'UPI', 'HDFC Salary', NULL, 'Mobile recharge', NULL, 'bills,mobile'),
('2024-10-12', 2, 'Debit', 'Bills & Utilities', 'Jio', 399, 'Expense', 'UPI', 'ICICI Salary', NULL, 'Mobile recharge', NULL, 'bills,mobile'),

-- Groceries & Food
('2024-10-06', 2, 'Debit', 'Groceries', 'BigBasket', 4500, 'Expense', 'UPI', 'ICICI Salary', NULL, 'Weekly groceries', NULL, 'groceries,food'),
('2024-10-13', 2, 'Debit', 'Groceries', 'DMart', 3800, 'Expense', 'Debit Card', 'ICICI Salary', NULL, 'Weekly groceries', NULL, 'groceries,food'),
('2024-10-15', 1, 'Debit', 'Food & Dining', 'Swiggy', 850, 'Expense', 'Credit Card', 'HDFC Credit Card', NULL, 'Dinner order', NULL, 'food,delivery'),
('2024-10-20', 2, 'Debit', 'Groceries', 'Zepto', 2200, 'Expense', 'UPI', 'ICICI Salary', NULL, 'Weekly groceries', NULL, 'groceries,food'),
('2024-10-22', 1, 'Debit', 'Food & Dining', 'Zomato', 1200, 'Expense', 'Credit Card', 'HDFC Credit Card', NULL, 'Office lunch', NULL, 'food,delivery'),
('2024-10-27', 2, 'Debit', 'Groceries', 'BigBasket', 5100, 'Expense', 'UPI', 'ICICI Salary', NULL, 'Monthly stock up', NULL, 'groceries,food'),

-- Transportation
('2024-10-07', 1, 'Debit', 'Transportation', 'Indian Oil', 4000, 'Expense', 'Credit Card', 'HDFC Credit Card', NULL, 'Petrol', NULL, 'fuel,transport'),
('2024-10-18', 1, 'Debit', 'Transportation', 'Uber', 450, 'Expense', 'UPI', 'HDFC Salary', NULL, 'Office commute', NULL, 'cab,transport'),
('2024-10-25', 1, 'Debit', 'Transportation', 'Indian Oil', 3500, 'Expense', 'Credit Card', 'HDFC Credit Card', NULL, 'Petrol', NULL, 'fuel,transport'),

-- Shopping
('2024-10-14', 2, 'Debit', 'Shopping', 'Amazon', 2999, 'Expense', 'Credit Card', 'ICICI Credit Card', NULL, 'Kitchen appliance', NULL, 'shopping,home'),
('2024-10-19', 3, 'Debit', 'Shopping', 'Decathlon', 3500, 'Expense', 'Debit Card', 'HDFC Salary', NULL, 'Sports shoes', NULL, 'shopping,sports'),
('2024-10-28', 2, 'Debit', 'Shopping', 'Myntra', 4200, 'Expense', 'Credit Card', 'ICICI Credit Card', NULL, 'Diwali clothes', NULL, 'shopping,clothes'),

-- Entertainment
('2024-10-12', 1, 'Debit', 'Entertainment', 'Netflix', 649, 'Expense', 'Auto Debit', 'HDFC Credit Card', NULL, 'Monthly subscription', NULL, 'entertainment,subscription'),
('2024-10-12', 1, 'Debit', 'Entertainment', 'Spotify', 119, 'Expense', 'Auto Debit', 'HDFC Credit Card', NULL, 'Monthly subscription', NULL, 'entertainment,subscription'),
('2024-10-20', 1, 'Debit', 'Entertainment', 'PVR Cinemas', 1400, 'Expense', 'UPI', 'HDFC Salary', NULL, 'Movie tickets', NULL, 'entertainment,movies'),

-- Health
('2024-10-15', 1, 'Debit', 'Health', 'Apollo Pharmacy', 1200, 'Expense', 'UPI', 'HDFC Salary', NULL, 'Medicines', NULL, 'health,pharmacy'),
('2024-10-22', 2, 'Debit', 'Health', 'Cult.fit', 2500, 'Expense', 'Auto Debit', 'ICICI Salary', NULL, 'Gym membership', NULL, 'health,fitness'),

-- Bot expenses
('2024-10-05', 3, 'Debit', 'Education', 'Module', 25000, 'Expense', 'Bank Transfer', 'HDFC Salary', NULL, 'School fees Q3', NULL, 'education,school'),
('2024-10-16', 3, 'Debit', 'Education', 'Maitance', 3000, 'Expense', 'Auto Debit', 'HDFC Salary', NULL, 'Online tuition', NULL, 'education,tuition'),

-- Miscellaneous
('2024-10-25', 1, 'Debit', 'Insurance', 'ICICI Prudential', 15000, 'Expense', 'Auto Debit', 'HDFC Salary', NULL, 'Term insurance premium', NULL, 'insurance,term'),
('2024-10-30', 1, 'Debit', 'Savings', 'HDFC Bank', 20000, 'Savings', 'Bank Transfer', 'HDFC Salary', 3, 'Car fund transfer', 'Monthly car fund', 'savings,car'),

-- November 2024
('2024-11-01', 1, 'Credit', 'Salary', 'TechCorp India', 185000, 'Income', 'Bank Transfer', 'HDFC Salary', NULL, 'November salary', NULL, 'salary,income'),
('2024-11-05', 2, 'Credit', 'Salary', 'InfoSys Ltd', 95000, 'Income', 'Bank Transfer', 'ICICI Salary', NULL, 'November salary', NULL, 'salary,income'),
('2024-11-02', 1, 'Debit', 'Investment', 'Zerodha', 25000, 'Investment', 'Auto Debit', 'HDFC Salary', 1, 'SIP - Nifty 50 Index', 'Monthly SIP', 'sip,mutual-fund'),
('2024-11-02', 1, 'Debit', 'Investment', 'Zerodha', 15000, 'Investment', 'Auto Debit', 'HDFC Salary', 1, 'SIP - Midcap Fund', 'Monthly SIP', 'sip,mutual-fund'),
('2024-11-05', 1, 'Debit', 'Investment', 'Kuvera', 10000, 'Investment', 'Auto Debit', 'ICICI Salary', 2, 'Liquid Fund - Emergency', NULL, 'liquid-fund,emergency'),
('2024-11-05', 1, 'Debit', 'EMI', 'HDFC Home Loan', 42000, 'Expense', 'Auto Debit', 'HDFC Salary', NULL, 'Home loan EMI', NULL, 'emi,home-loan'),
('2024-11-10', 2, 'Debit', 'EMI', 'Bajaj Finance', 8500, 'Expense', 'Auto Debit', 'ICICI Salary', NULL, 'iPhone EMI', NULL, 'emi,phone'),
('2024-11-08', 1, 'Debit', 'Bills & Utilities', 'Adani Electricity', 2800, 'Expense', 'Auto Debit', 'HDFC Salary', NULL, 'Electricity bill', NULL, 'bills,electricity'),
('2024-11-10', 1, 'Debit', 'Bills & Utilities', 'Mahanagar Gas', 1600, 'Expense', 'UPI', 'HDFC Salary', NULL, 'Gas bill', NULL, 'bills,gas'),
('2024-11-12', 1, 'Debit', 'Bills & Utilities', 'Jio Fiber', 1499, 'Expense', 'Auto Debit', 'HDFC Salary', NULL, 'Internet + TV', NULL, 'bills,internet'),

-- Diwali expenses
('2024-11-01', 2, 'Debit', 'Shopping', 'Tanishq', 45000, 'Expense', 'Credit Card', 'HDFC Credit Card', NULL, 'Diwali jewellery', 'Festival purchase', 'shopping,diwali,jewellery'),
('2024-11-02', 1, 'Debit', 'Shopping', 'Amazon', 12000, 'Expense', 'Credit Card', 'HDFC Credit Card', NULL, 'Diwali gifts', NULL, 'shopping,diwali,gifts'),
('2024-11-03', 2, 'Debit', 'Food & Dining', 'Haldirams', 3500, 'Expense', 'UPI', 'ICICI Salary', NULL, 'Diwali sweets', NULL, 'food,diwali'),
('2024-11-04', 1, 'Debit', 'Shopping', 'Local Market', 5000, 'Expense', 'Cash', 'Cash', NULL, 'Diwali crackers & decor', NULL, 'shopping,diwali'),

-- Regular November expenses
('2024-11-06', 2, 'Debit', 'Groceries', 'BigBasket', 6200, 'Expense', 'UPI', 'ICICI Salary', NULL, 'Weekly groceries', NULL, 'groceries,food'),
('2024-11-13', 2, 'Debit', 'Groceries', 'DMart', 4100, 'Expense', 'Debit Card', 'ICICI Salary', NULL, 'Weekly groceries', NULL, 'groceries,food'),
('2024-11-20', 2, 'Debit', 'Groceries', 'Zepto', 2800, 'Expense', 'UPI', 'ICICI Salary', NULL, 'Weekly groceries', NULL, 'groceries,food'),
('2024-11-27', 2, 'Debit', 'Groceries', 'BigBasket', 4500, 'Expense', 'UPI', 'ICICI Salary', NULL, 'Weekly groceries', NULL, 'groceries,food'),
('2024-11-10', 1, 'Debit', 'Transportation', 'Indian Oil', 4200, 'Expense', 'Credit Card', 'HDFC Credit Card', NULL, 'Petrol', NULL, 'fuel,transport'),
('2024-11-22', 1, 'Debit', 'Transportation', 'HP Petrol', 3800, 'Expense', 'Credit Card', 'HDFC Credit Card', NULL, 'Petrol', NULL, 'fuel,transport'),
('2024-11-12', 1, 'Debit', 'Entertainment', 'Netflix', 649, 'Expense', 'Auto Debit', 'HDFC Credit Card', NULL, 'Monthly subscription', NULL, 'entertainment,subscription'),
('2024-11-12', 1, 'Debit', 'Entertainment', 'Spotify', 119, 'Expense', 'Auto Debit', 'HDFC Credit Card', NULL, 'Monthly subscription', NULL, 'entertainment,subscription'),
('2024-11-15', 1, 'Debit', 'Food & Dining', 'Mainland China', 4500, 'Expense', 'Credit Card', 'HDFC Credit Card', NULL, 'Anniversary dinner', NULL, 'food,dining'),
('2024-11-16', 3, 'Debit', 'Education', 'Byju''s', 3000, 'Expense', 'Auto Debit', 'HDFC Salary', NULL, 'Online tuition', NULL, 'education,tuition'),
('2024-11-18', 2, 'Debit', 'Health', 'Max Hospital', 2500, 'Expense', 'Credit Card', 'ICICI Credit Card', NULL, 'Health checkup', NULL, 'health,medical'),
('2024-11-22', 2, 'Debit', 'Health', 'Cult.fit', 2500, 'Expense', 'Auto Debit', 'ICICI Salary', NULL, 'Gym membership', NULL, 'health,fitness'),
('2024-11-25', 1, 'Credit', 'Bonus', 'TechCorp India', 50000, 'Income', 'Bank Transfer', 'HDFC Salary', NULL, 'Diwali bonus', NULL, 'bonus,income'),
('2024-11-26', 1, 'Debit', 'Investment', 'Zerodha', 30000, 'Investment', 'Bank Transfer', 'HDFC Salary', 1, 'Bonus investment', 'Lump sum from bonus', 'investment,bonus'),
('2024-11-30', 1, 'Debit', 'Savings', 'HDFC Bank', 20000, 'Savings', 'Bank Transfer', 'HDFC Salary', 3, 'Car fund transfer', 'Monthly car fund', 'savings,car'),
('2024-11-28', 2, 'Debit', 'Savings', 'ICICI Bank', 10000, 'Savings', 'Bank Transfer', 'ICICI Salary', 4, 'Vacation fund', 'Europe trip saving', 'savings,vacation'),

-- December 2024
('2024-12-01', 1, 'Credit', 'Salary', 'TechCorp India', 185000, 'Income', 'Bank Transfer', 'HDFC Salary', NULL, 'December salary', NULL, 'salary,income'),
('2024-12-05', 2, 'Credit', 'Salary', 'InfoSys Ltd', 95000, 'Income', 'Bank Transfer', 'ICICI Salary', NULL, 'December salary', NULL, 'salary,income'),
('2024-12-02', 1, 'Debit', 'Investment', 'Zerodha', 25000, 'Investment', 'Auto Debit', 'HDFC Salary', 1, 'SIP - Nifty 50 Index', 'Monthly SIP', 'sip,mutual-fund'),
('2024-12-02', 1, 'Debit', 'Investment', 'Zerodha', 15000, 'Investment', 'Auto Debit', 'HDFC Salary', 1, 'SIP - Midcap Fund', 'Monthly SIP', 'sip,mutual-fund'),
('2024-12-05', 1, 'Debit', 'Investment', 'Kuvera', 10000, 'Investment', 'Auto Debit', 'ICICI Salary', 2, 'Liquid Fund - Emergency', NULL, 'liquid-fund,emergency'),
('2024-12-05', 1, 'Debit', 'EMI', 'HDFC Home Loan', 42000, 'Expense', 'Auto Debit', 'HDFC Salary', NULL, 'Home loan EMI', NULL, 'emi,home-loan'),
('2024-12-05', 1, 'Debit', 'EMI', 'HDFC Home Loan', 100000, 'Expense', 'Bank Transfer', 'HDFC Salary', 5, 'Home loan prepayment', 'Year end prepayment', 'emi,home-loan,prepayment'),
('2024-12-06', 2, 'Debit', 'Groceries', 'BigBasket', 5500, 'Expense', 'UPI', 'ICICI Salary', NULL, 'Weekly groceries', NULL, 'groceries,food'),
('2024-12-07', 1, 'Debit', 'Transportation', 'Indian Oil', 4000, 'Expense', 'Credit Card', 'HDFC Credit Card', NULL, 'Petrol', NULL, 'fuel,transport');
