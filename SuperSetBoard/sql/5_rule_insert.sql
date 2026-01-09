-- =============================================================================
-- CATEGORIZATION RULES SEED DATA
-- =============================================================================
-- Run this after creating tables with rule_schema.sql
--
-- DSL Syntax: rule "Name" where <conditions> assign <assignments> priority N;
-- Operators: eq, neq, gt, lt, gte, lte, between, con, noc, sw, ew, regex, in, nin, null, nnull
-- Add :i for case-insensitive matching
-- Assignments: category_id, tag_id, type_id, payment_method_id, goal_id
-- =============================================================================

BEGIN;

-- Clear existing rules (optional - uncomment if needed)
-- TRUNCATE TABLE ss_categorization_rules RESTART IDENTITY;

INSERT INTO ss_categorization_rules (name, dsl_text, priority, user_id, is_active) VALUES

-- =============================================================================
-- PAYMENT METHOD DETECTION (Priority 100 - detect payment type first)
-- =============================================================================
('UPI Payment', 'rule "UPI Payment" where description:sw:"UPI":i assign payment_method_id:1 priority 100;', 100, 1, TRUE),
('NEFT Payment', 'rule "NEFT Payment" where description:sw:"NEFT":i assign payment_method_id:10 priority 100;', 100, 1, TRUE),
('IMPS Payment', 'rule "IMPS Payment" where description:sw:"IMPS":i assign payment_method_id:3 priority 100;', 100, 1, TRUE),
('NACH Payment', 'rule "NACH Payment" where description:sw:"NACH":i assign payment_method_id:9 priority 100;', 100, 1, TRUE),
('RTGS Payment', 'rule "RTGS Payment" where description:sw:"RTGS":i assign payment_method_id:7 priority 100;', 100, 1, TRUE),

-- =============================================================================
-- INCOME RULES (Priority 10-20 - high priority for income classification)
-- =============================================================================
-- Salary
('Salary Credit', 'rule "Salary Credit" where description:regex:"SALARY|PAYROLL":i and type:eq:"credit":i assign category_id:1 type_id:1 priority 10;', 10, 1, TRUE),
('Interest Credit','rule "Interest Credit" where description:con:"INT.PD":i and type:eq:"credit":i assign category_id:1 type_id:1 priority 12;',12, 1, TRUE),

-- Freelance Income (Wise, Skydo, etc.)
('Wise Income', 'rule "Wise Income" where description:regex:"WISE|NEFT.WISE PAYMENTS|ESCROW":i and type:eq:"credit":i assign category_id:2 type_id:1 priority 15;', 15, 1, TRUE),
('Skydo Income', 'rule "Skydo Income" where description:con:"SKYDO":i and type:eq:"credit":i assign category_id:2 type_id:1 priority 15;', 15, 1, TRUE),

-- =============================================================================
-- INVESTMENT RULES (Priority 15-25)
-- =============================================================================
-- SIP / Mutual Funds
('Investment SIP', 'rule "Investment SIP" where entity_name:sw:"Indian Cle":i and type:eq:"debit" and payment_method:sw:"NACH":i assign category_id:3 type_id:2 goal_id:1 tag_id:1 priority 15;', 15, 1, TRUE),
('Investment - MF/SIP', 'rule "Investment - MF/SIP" where description:regex:"MUTUALFUND|MF|SIP|GROWW|ZERODHA|KUVERA":i and type:eq:"debit":i assign category_id:3 type_id:2 priority 20;', 20, 1, TRUE),

-- Stocks/Demat
('Investment - Stocks', 'rule "Investment - Stocks" where description:regex:"STOCK|SHARES|DEMAT|CDSL|NSDL":i and type:eq:"debit":i assign category_id:3 type_id:2 priority 20;', 20, 1, TRUE),

-- =============================================================================
-- INSURANCE RULES (Priority 60)
-- =============================================================================
('Term Insurance', 'rule "Term Insurance" where description:regex:"TERM INSURANCE|TERM PLAN|LIC|HDFC LIFE|ICICI PRU|SBI LIFE|MAX LIFE":i and type:eq:"debit":i assign category_id:4 type_id:2 priority 60;', 60, 1, TRUE),
('Health Insurance', 'rule "Health Insurance" where description:regex:"HEALTH INSURANCE|MEDICLAIM|STAR HEALTH|CARE HEALTH|NIVA BUPA|ADITYA BIRLA HEALTH":i and type:eq:"debit":i assign category_id:11 type_id:2 priority 60;', 60, 1, TRUE),

-- =============================================================================
-- EMI RULES (Priority 25)
-- =============================================================================
('Home Loan EMI', 'rule "Home Loan EMI" where description:regex:"HOME LOAN|HOUSING LOAN|SBI HOME|HDFC HOME":i and type:eq:"debit":i assign category_id:5 type_id:2 tag_id:4 priority 25;', 25, 1, TRUE),

-- =============================================================================
-- CASH/ATM RULES (Priority 30)
-- =============================================================================
('ATM Withdrawal', 'rule "ATM Withdrawal" where description:con:"ATM","CASH WDL","CASH WITHDRAWAL":i assign category_id:6 payment_method_id:4 type_id:2 priority 30;', 30, 1, TRUE),

-- =============================================================================
-- TRANSFER RULES (Priority 50)
-- =============================================================================
('Transfer - Self', 'rule "Transfer - Self" where description:regex:"NISHANT|SELF|OWN ACCOUNT|TRANSFER TO SELF":i assign category_id:10 type_id:3 priority 50;', 50, 1, TRUE),

-- =============================================================================
-- FAMILY TRANSFERS (Priority 10 - high priority to catch before generic transfers)
-- =============================================================================
('Family - Kanti', 'rule "Family - Kanti" where entity_name:regex:"KANTI|POOJA":i assign category_id:10 tag_id:1 priority 10;', 10, 1, TRUE),

-- =============================================================================
-- UTILITY BILLS (Priority 40)
-- =============================================================================
('Utility - Electricity', 'rule "Utility - Electricity" where description:regex:"ELECTRICITY|POWER|MSEDCL|TATA POWER|ADANI":i and type:eq:"debit":i assign category_id:6 type_id:2 tag_id:3 priority 40;', 40, 1, TRUE),
('Utility - Gas', 'rule "Utility - Gas" where description:regex:"GAS BILL|PNG|MAHANAGAR GAS|IGL":i and type:eq:"debit":i assign category_id:6 type_id:2 tag_id:3 priority 40;', 40, 1, TRUE),
('Utility - Mobile', 'rule "Utility - Mobile" where description:regex:"AIRTEL|JIO|VODAFONE|VI|BSNL|MOBILE RECHARGE":i and type:eq:"debit":i assign category_id:6 type_id:2 tag_id:3 priority 40;', 40, 1, TRUE),
('Utility - Internet', 'rule "Utility - Internet" where description:regex:"BROADBAND|INTERNET|WIFI|ACT FIBERNET":i and type:eq:"debit":i assign category_id:6 type_id:2 tag_id:3 priority 40;', 40, 1, TRUE),

-- =============================================================================
-- TAGGING RULES (Priority 100)
-- =============================================================================
('Large Transaction > 50k', 'rule "Large Transaction" where amount:gt:"50000" assign tag_id:2 priority 100;', 100, 1, TRUE),

-- =============================================================================
-- FALLBACK TYPE RULES (Priority 200 - lowest priority, catch-all)
-- =============================================================================
('Type - Credit Fallback', 'rule "Type - Credit Fallback" where type:eq:"credit":i assign type_id:1 priority 200;', 200, 1, TRUE),
('Type - Debit Fallback', 'rule "Type - Debit Fallback" where type:eq:"debit":i assign type_id:2 priority 200;', 200, 1, TRUE);


COMMIT;
