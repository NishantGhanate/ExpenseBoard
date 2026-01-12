#!/usr/bin/env python3
"""
Test AND/OR logic with dynamic field assignments

This demonstrates:
1. Simple AND conditions
2. Simple OR conditions
3. Complex (AND and OR) combinations
4. Custom field assignments with each

> source .env
> python ./app/rule_engine/new_example.py
"""

from decimal import Decimal

from app.rule_engine.evaluator import TransactionCategorizer
from app.rule_engine.parser import parse_rules

print("=" * 70)
print("TEST: AND/OR Logic with Dynamic Field Assignment")
print("=" * 70)
print()

# =============================================================================
# TEST 1: Simple AND logic
# =============================================================================
print("TEST 1: Simple AND Logic")
print("-" * 70)

dsl_and = '''
rule "High Value Family Transfer"
    where entity_name:con:"KANTI":i or amount:gt:"50000"
    assign category_id:1
           risk_level:2
           alert_type:"HIGH_VALUE_FAMILY"
           needs_review:0
           priority 10;
'''

rules = parse_rules(dsl_and)
categorizer = TransactionCategorizer(rules)

# Test case 1.1: Both conditions match
tx1 = {
    "entity_name": "KANTI RAMULU GA",
    "amount": Decimal("75000.00")
}

result1 = categorizer.categorize(tx1)
print("Transaction 1: Both conditions match (KANTI + amount > 50000)")
print(f"  entity_name: {tx1['entity_name']}")
print(f"  amount: {tx1['amount']}")
print(f"  ✓ Rule matched: {len(categorizer.find_matching_rules(tx1)) > 0}")
print(f"  category_id: {result1.get('category_id')}")
print(f"  risk_level: {result1.get('risk_level')}")
print(f"  alert_type: {result1.get('alert_type')}")
print(f"  needs_review: {result1.get('needs_review')}")
print()

# Test case 1.2: Only first condition matches
tx2 = {
    "entity_name": "KANTI RAMULU GA",
    "amount": Decimal("25000.00"),
    "type_id":2
}

result2 = categorizer.categorize(tx2)
print("Transaction 2: Only first condition matches (KANTI + amount <= 50000)")
print(f"  entity_name: {tx2['entity_name']}")
print(f"  amount: {tx2['amount']}")
print(f"  ✗ Rule matched: {len(categorizer.find_matching_rules(tx2)) > 0}")
print(f"  category_id: {result2.get('category_id')}")
print(f"  risk_level: {result2.get('risk_level')}")
print()

# Test case 1.3: Only second condition matches
tx3 = {
    "entity_name": "SOME OTHER PERSON",
    "amount": Decimal("75000.00")
}

result3 = categorizer.categorize(tx3)
print("Transaction 3: Only second condition matches (not KANTI + amount > 50000)")
print(f"  entity_name: {tx3['entity_name']}")
print(f"  amount: {tx3['amount']}")
print(f"  ✗ Rule matched: {len(categorizer.find_matching_rules(tx3)) > 0}")
print(f"  category_id: {result3.get('category_id')}")
print()

# # =============================================================================
# # TEST 2: Simple OR logic
# # =============================================================================
# print("=" * 70)
# print("TEST 2: Simple OR Logic")
# print("-" * 70)

# dsl_or = '''
# rule "Family OR High Value"
#     where entity_name:con:"KANTI":i or amount:gt:"50000"
#     assign category_id:2
#            risk_level:1
#            alert_type:"FAMILY_OR_HIGH_VALUE"
#            priority 20;
# '''

# rules = parse_rules(dsl_or)
# categorizer = TransactionCategorizer(rules)

# # Test case 2.1: Both conditions match
# tx1 = {
#     "entity_name": "KANTI RAMULU GA",
#     "amount": Decimal("75000.00")
# }

# result1 = categorizer.categorize(tx1)
# print("Transaction 1: Both conditions match (KANTI OR amount > 50000)")
# print(f"  entity_name: {tx1['entity_name']}")
# print(f"  amount: {tx1['amount']}")
# print(f"  ✓ Rule matched: {len(categorizer.find_matching_rules(tx1)) > 0}")
# print(f"  category_id: {result1.get('category_id')}")
# print(f"  risk_level: {result1.get('risk_level')}")
# print(f"  alert_type: {result1.get('alert_type')}")
# print()

# # Test case 2.2: Only first condition matches
# tx2 = {
#     "entity_name": "KANTI RAMULU GA",
#     "amount": Decimal("25000.00")
# }

# result2 = categorizer.categorize(tx2)
# print("Transaction 2: Only first condition matches (KANTI OR amount <= 50000)")
# print(f"  entity_name: {tx2['entity_name']}")
# print(f"  amount: {tx2['amount']}")
# print(f"  ✓ Rule matched: {len(categorizer.find_matching_rules(tx2)) > 0}")
# print(f"  category_id: {result2.get('category_id')}")
# print(f"  alert_type: {result2.get('alert_type')}")
# print()

# # Test case 2.3: Only second condition matches
# tx3 = {
#     "entity_name": "SOME OTHER PERSON",
#     "amount": Decimal("75000.00")
# }

# result3 = categorizer.categorize(tx3)
# print("Transaction 3: Only second condition matches (not KANTI OR amount > 50000)")
# print(f"  entity_name: {tx3['entity_name']}")
# print(f"  amount: {tx3['amount']}")
# print(f"  ✓ Rule matched: {len(categorizer.find_matching_rules(tx3)) > 0}")
# print(f"  category_id: {result3.get('category_id')}")
# print(f"  alert_type: {result3.get('alert_type')}")
# print()

# # Test case 2.4: Neither condition matches
# tx4 = {
#     "entity_name": "SOME OTHER PERSON",
#     "amount": Decimal("25000.00")
# }

# result4 = categorizer.categorize(tx4)
# print("Transaction 4: Neither condition matches (not KANTI OR amount <= 50000)")
# print(f"  entity_name: {tx4['entity_name']}")
# print(f"  amount: {tx4['amount']}")
# print(f"  ✗ Rule matched: {len(categorizer.find_matching_rules(tx4)) > 0}")
# print(f"  category_id: {result4.get('category_id')}")
# print()

# # =============================================================================
# # TEST 3: Complex AND + OR logic
# # =============================================================================
# print("=" * 70)
# print("TEST 3: Complex AND + OR Logic")
# print("-" * 70)

# dsl_complex = '''
# rule "Complex Rule"
#     where entity_name:con:"KANTI":i and amount:gt:"50000"
#        or description:con:"SALARY":i and _raw_type:eq:"credit"
#     assign category_id:3
#            classification:"INCOME_OR_FAMILY"
#            risk_score:75
#            alert_flag:1
#            processing_status:"AUTO_APPROVED"
#            priority 30;
# '''

# print("Rule Logic: (KANTI AND amount > 50000) OR (SALARY AND type = credit)")
# print()

# rules = parse_rules(dsl_complex)
# categorizer = TransactionCategorizer(rules)

# # Test case 3.1: First OR block matches (KANTI + high amount)
# tx1 = {
#     "entity_name": "KANTI RAMULU GA",
#     "amount": Decimal("75000.00"),
#     "description": "Transfer to family",
#     "_raw_type": "debit"
# }

# result1 = categorizer.categorize(tx1)
# print("Transaction 1: First OR block matches (KANTI + amount > 50000)")
# print(f"  entity_name: {tx1['entity_name']}")
# print(f"  amount: {tx1['amount']}")
# print(f"  description: {tx1['description']}")
# print(f"  _raw_type: {tx1['_raw_type']}")
# print(f"  ✓ Rule matched: {len(categorizer.find_matching_rules(tx1)) > 0}")
# print(f"  category_id: {result1.get('category_id')}")
# print(f"  classification: {result1.get('classification')}")
# print(f"  risk_score: {result1.get('risk_score')}")
# print(f"  alert_flag: {result1.get('alert_flag')}")
# print(f"  processing_status: {result1.get('processing_status')}")
# print()

# # Test case 3.2: Second OR block matches (SALARY + credit)
# tx2 = {
#     "entity_name": "EMPLOYER INC",
#     "amount": Decimal("100000.00"),
#     "description": "SALARY CREDIT FOR DECEMBER",
#     "_raw_type": "credit"
# }

# result2 = categorizer.categorize(tx2)
# print("Transaction 2: Second OR block matches (SALARY + type = credit)")
# print(f"  entity_name: {tx2['entity_name']}")
# print(f"  amount: {tx2['amount']}")
# print(f"  description: {tx2['description']}")
# print(f"  _raw_type: {tx2['_raw_type']}")
# print(f"  ✓ Rule matched: {len(categorizer.find_matching_rules(tx2)) > 0}")
# print(f"  category_id: {result2.get('category_id')}")
# print(f"  classification: {result2.get('classification')}")
# print(f"  risk_score: {result2.get('risk_score')}")
# print()

# # Test case 3.3: Both OR blocks match
# tx3 = {
#     "entity_name": "KANTI SALARY DEPT",
#     "amount": Decimal("150000.00"),
#     "description": "SALARY PAYMENT",
#     "_raw_type": "credit"
# }

# result3 = categorizer.categorize(tx3)
# print("Transaction 3: Both OR blocks match")
# print(f"  entity_name: {tx3['entity_name']}")
# print(f"  amount: {tx3['amount']}")
# print(f"  description: {tx3['description']}")
# print(f"  _raw_type: {tx3['_raw_type']}")
# print(f"  ✓ Rule matched: {len(categorizer.find_matching_rules(tx3)) > 0}")
# print(f"  category_id: {result3.get('category_id')}")
# print()

# # Test case 3.4: Partial matches but neither OR block fully matches
# tx4 = {
#     "entity_name": "KANTI RAMULU GA",  # Matches first part of first block
#     "amount": Decimal("25000.00"),      # Doesn't match second part
#     "description": "Regular transfer",
#     "_raw_type": "debit"
# }

# result4 = categorizer.categorize(tx4)
# print("Transaction 4: Partial matches but no OR block fully matches")
# print(f"  entity_name: {tx4['entity_name']} (matches KANTI)")
# print(f"  amount: {tx4['amount']} (doesn't match > 50000)")
# print(f"  description: {tx4['description']} (doesn't match SALARY)")
# print(f"  _raw_type: {tx4['_raw_type']} (doesn't match credit)")
# print(f"  ✗ Rule matched: {len(categorizer.find_matching_rules(tx4)) > 0}")
# print(f"  category_id: {result4.get('category_id')}")
# print()

# # =============================================================================
# # TEST 4: Multiple rules with priority
# # =============================================================================
# print("=" * 70)
# print("TEST 4: Multiple Rules with Priority and Custom Fields")
# print("-" * 70)

# dsl_multi = '''
# rule "High Priority - Family High Value"
#     where entity_name:con:"KANTI":i and amount:gt:"100000"
#     assign category_id:1
#            priority_level:"CRITICAL"
#            review_by:"MANAGER"
#            alert_channels:"SMS,EMAIL,APP"
#            risk_score:95
#            priority 5;

# rule "Medium Priority - Family"
#     where entity_name:con:"KANTI":i
#     assign category_id:2
#            priority_level:"NORMAL"
#            review_by:"SYSTEM"
#            alert_channels:"EMAIL"
#            risk_score:50
#            priority 10;

# rule "Low Priority - Large Amount"
#     where amount:gt:"100000"
#     assign category_id:3
#            priority_level:"MEDIUM"
#            review_by:"ANALYST"
#            alert_channels:"EMAIL,APP"
#            risk_score:70
#            priority 15;
# '''

# rules = parse_rules(dsl_multi)
# categorizer = TransactionCategorizer(rules)

# # Transaction matches multiple rules - first by priority wins
# tx = {
#     "entity_name": "KANTI RAMULU GA",
#     "amount": Decimal("150000.00")
# }

# result = categorizer.categorize(tx)
# matching_rules = categorizer.find_matching_rules(tx)

# print("Transaction matches multiple rules:")
# print(f"  entity_name: {tx['entity_name']}")
# print(f"  amount: {tx['amount']}")
# print()
# print(f"Matching rules (in order of priority):")
# for rule in matching_rules:
#     print(f"  - {rule.name} (priority: {rule.priority})")
# print()
# print("Applied values (from highest priority rule):")
# print(f"  category_id: {result.get('category_id')}")
# print(f"  priority_level: {result.get('priority_level')}")
# print(f"  review_by: {result.get('review_by')}")
# print(f"  alert_channels: {result.get('alert_channels')}")
# print(f"  risk_score: {result.get('risk_score')}")
# print()

# # =============================================================================
# # TEST 5: Triple condition with AND + OR
# # =============================================================================
# print("=" * 70)
# print("TEST 5: Triple Condition - (A AND B AND C) OR D")
# print("-" * 70)

# dsl_triple = '''
# rule "High Risk International"
#     where amount:gt:"50000" and description:con:"SWIFT","FOREIGN":i and _raw_type:eq:"debit"
#        or description:con:"CRYPTO","BITCOIN":i
#     assign category_id:10
#            risk_category:"HIGH_RISK"
#            compliance_required:1
#            verification_level:3
#            hold_period_hours:48
#            assigned_team:"FRAUD_PREVENTION"
#            status:"UNDER_REVIEW"
#            priority 1;
# '''

# print("Rule Logic: (amount > 50000 AND SWIFT/FOREIGN AND debit) OR CRYPTO/BITCOIN")
# print()

# rules = parse_rules(dsl_triple)
# categorizer = TransactionCategorizer(rules)

# # Test case 5.1: First OR block (all 3 ANDs match)
# tx1 = {
#     "amount": Decimal("75000.00"),
#     "description": "SWIFT INTERNATIONAL TRANSFER",
#     "_raw_type": "debit"
# }

# result1 = categorizer.categorize(tx1)
# print("Transaction 1: International debit > 50000 (all 3 ANDs match)")
# print(f"  amount: {tx1['amount']}")
# print(f"  description: {tx1['description']}")
# print(f"  _raw_type: {tx1['_raw_type']}")
# print(f"  ✓ Rule matched: {len(categorizer.find_matching_rules(tx1)) > 0}")
# print(f"  category_id: {result1.get('category_id')}")
# print(f"  risk_category: {result1.get('risk_category')}")
# print(f"  compliance_required: {result1.get('compliance_required')}")
# print(f"  verification_level: {result1.get('verification_level')}")
# print(f"  hold_period_hours: {result1.get('hold_period_hours')}")
# print(f"  assigned_team: {result1.get('assigned_team')}")
# print(f"  status: {result1.get('status')}")
# print()

# # Test case 5.2: Second OR block (crypto)
# tx2 = {
#     "amount": Decimal("5000.00"),
#     "description": "CRYPTO EXCHANGE - BITCOIN PURCHASE",
#     "_raw_type": "debit"
# }

# result2 = categorizer.categorize(tx2)
# print("Transaction 2: Crypto transaction (second OR block)")
# print(f"  amount: {tx2['amount']}")
# print(f"  description: {tx2['description']}")
# print(f"  _raw_type: {tx2['_raw_type']}")
# print(f"  ✓ Rule matched: {len(categorizer.find_matching_rules(tx2)) > 0}")
# print(f"  category_id: {result2.get('category_id')}")
# print(f"  risk_category: {result2.get('risk_category')}")
# print(f"  assigned_team: {result2.get('assigned_team')}")
# print()

# # Test case 5.3: Partial match (only 2 of 3 ANDs)
# tx3 = {
#     "amount": Decimal("75000.00"),
#     "description": "SWIFT INTERNATIONAL TRANSFER",
#     "_raw_type": "credit"  # Wrong type!
# }

# result3 = categorizer.categorize(tx3)
# print("Transaction 3: Partial match (amount + SWIFT but credit not debit)")
# print(f"  amount: {tx3['amount']}")
# print(f"  description: {tx3['description']}")
# print(f"  _raw_type: {tx3['_raw_type']}")
# print(f"  ✗ Rule matched: {len(categorizer.find_matching_rules(tx3)) > 0}")
# print(f"  category_id: {result3.get('category_id')}")
# print()

# print("=" * 70)
# print("✅ ALL AND/OR TESTS COMPLETED!")
# print("=" * 70)
