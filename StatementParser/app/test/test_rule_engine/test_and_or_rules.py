from decimal import Decimal

import pytest
from app.rule_engine.evaluator import TransactionCategorizer
from app.rule_engine.parser import parse_rules


class TestTransactionCategorizer:

    # -------------------------------------------------------------------------
    # TEST 1: Simple AND Logic
    # -------------------------------------------------------------------------
    @pytest.mark.parametrize("tx, expected_match, expected_category", [
        # 1.1: Both conditions match
        ({"entity_name": "KANTI RAMULU GA", "amount": Decimal("75000.00")}, True, 1),
        # 1.2: Only first condition matches
        ({"entity_name": "KANTI RAMULU GA", "amount": Decimal("25000.00")}, False, None),
        # 1.3: Only second condition matches
        ({"entity_name": "SOME OTHER PERSON", "amount": Decimal("75000.00")}, False, None),
    ])
    def test_simple_and_logic(self, tx, expected_match, expected_category):
        dsl_and = '''
        rule "High Value Family Transfer"
            where entity_name:con:"KANTI":i and amount:gt:"50000"
            assign category_id:1
                   risk_level:2
                   alert_type:"HIGH_VALUE_FAMILY"
                   needs_review:0
                   priority 10;
        '''
        rules = parse_rules(dsl_and)
        categorizer = TransactionCategorizer(rules)

        result = categorizer.categorize(tx)
        is_matched = len(categorizer.find_matching_rules(tx)) > 0

        assert is_matched == expected_match
        assert result.get('category_id') == expected_category
        if expected_match:
            assert result.get('risk_level') == 2
            assert result.get('alert_type') == "HIGH_VALUE_FAMILY"

    # -------------------------------------------------------------------------
    # TEST 2: Simple OR Logic
    # -------------------------------------------------------------------------
    @pytest.mark.parametrize("tx, expected_match", [
        ({"entity_name": "KANTI RAMULU GA", "amount": Decimal("75000.00")}, True),  # Both
        ({"entity_name": "KANTI RAMULU GA", "amount": Decimal("25000.00")}, True),  # First only
        ({"entity_name": "SOME OTHER PERSON", "amount": Decimal("75000.00")}, True), # Second only
        ({"entity_name": "SOME OTHER PERSON", "amount": Decimal("25000.00")}, False), # Neither
    ])
    def test_simple_or_logic(self, tx, expected_match):
        dsl_or = '''
        rule "Family OR High Value"
            where entity_name:con:"KANTI":i or amount:gt:"50000"
            assign category_id:2
                   risk_level:1
                   alert_type:"FAMILY_OR_HIGH_VALUE"
                   priority 20;
        '''
        rules = parse_rules(dsl_or)
        categorizer = TransactionCategorizer(rules)

        is_matched = len(categorizer.find_matching_rules(tx)) > 0
        assert is_matched == expected_match

        if expected_match:
            result = categorizer.categorize(tx)
            assert result.get('category_id') == 2

    # -------------------------------------------------------------------------
    # TEST 3: Complex AND + OR Logic
    # -------------------------------------------------------------------------
    @pytest.mark.parametrize("tx, expected_match", [
        # 3.1: First block (KANTI + High)
        ({"entity_name": "KANTI GA", "amount": Decimal("75000"), "description": "X", "_raw_type": "debit"}, True),
        # 3.2: Second block (Salary + Credit)
        ({"entity_name": "EMP", "amount": Decimal("100"), "description": "SALARY DEC", "_raw_type": "credit"}, True),
        # 3.4: Partial matches (No full block)
        ({"entity_name": "KANTI", "amount": Decimal("10"), "description": "X", "_raw_type": "debit"}, False),
    ])
    def test_complex_logic(self, tx, expected_match):
        dsl_complex = '''
        rule "Complex Rule"
            where entity_name:con:"KANTI":i and amount:gt:"50000"
               or description:con:"SALARY":i and _raw_type:eq:"credit"
            assign category_id:3
                   classification:"INCOME_OR_FAMILY"
                   priority 30;
        '''
        rules = parse_rules(dsl_complex)
        categorizer = TransactionCategorizer(rules)

        assert (len(categorizer.find_matching_rules(tx)) > 0) == expected_match

    # -------------------------------------------------------------------------
    # TEST 4: Priority
    # -------------------------------------------------------------------------
    def test_rule_priority(self):
        dsl_multi = '''
        rule "High Priority - Family High Value"
            where entity_name:con:"KANTI":i and amount:gt:"100000"
            assign category_id:1 priority 5;

        rule "Medium Priority - Family"
            where entity_name:con:"KANTI":i
            assign category_id:2 priority 10;
        '''
        rules = parse_rules(dsl_multi)
        categorizer = TransactionCategorizer(rules)

        tx = {"entity_name": "KANTI RAMULU", "amount": Decimal("150000.00")}

        result = categorizer.categorize(tx)
        matching = categorizer.find_matching_rules(tx)

        # Ensure multiple matches exist
        assert len(matching) >= 2
        # Ensure the one with lowest priority number (highest importance) wins
        assert result.get('category_id') == 1

    # -------------------------------------------------------------------------
    # TEST 5: Complex (A AND B) OR (C AND D)
    # -------------------------------------------------------------------------
    @pytest.mark.parametrize("tx, should_match, desc", [
        ({
            "entity_name": "KANTI RAMULU", "amount": Decimal("60000"),
            "description": "Transfer", "_raw_type": "debit"
        }, True, "First block match"),
        ({
            "entity_name": "EMPLOYER INC", "amount": Decimal("100000"),
            "description": "SALARY CREDIT", "_raw_type": "credit"
        }, True, "Second block match"),
        ({
            "entity_name": "KANTI RAMULU", "amount": Decimal("30000"),
            "description": "Transfer", "_raw_type": "debit"
        }, False, "Partial match failure"),
    ])
    def test_complex_and_or(self, tx, should_match, desc):
        dsl = '''
        rule "Complex Rule"
            where entity_name:con:"KANTI":i and amount:gt:"50000"
               or description:con:"SALARY":i and _raw_type:eq:"credit"
            assign category_id:3
                   classification:"INCOME_OR_FAMILY"
                   risk_score:75
                   processing_status:"AUTO_APPROVED"
                   priority 30;
        '''
        categorizer = TransactionCategorizer(parse_rules(dsl))
        result = categorizer.categorize(tx)

        assert (result.get('category_id') is not None) == should_match, f"Failed on: {desc}"
        if should_match:
            assert result.get('category_id') == 3
            assert result.get('classification') == "INCOME_OR_FAMILY"
            assert result.get('risk_score') == 75

    # -------------------------------------------------------------------------
    # TEST 6: Triple Condition - (A AND B AND C) OR D
    # -------------------------------------------------------------------------
    @pytest.mark.parametrize("tx, expected_match", [
        # 6.1: All 3 ANDs match
        ({"amount": Decimal("60000"), "description": "SWIFT X", "_raw_type": "debit"}, True),
        # 6.2: Crypto matches (OR block)
        ({"amount": Decimal("10"), "description": "BITCOIN", "_raw_type": "credit"}, True),
        # 6.3: Partial match (only 2 of 3)
        ({"amount": Decimal("60000"), "description": "SWIFT X", "_raw_type": "credit"}, False),
    ])
    def test_triple_condition(self, tx, expected_match):
        dsl_triple = '''
        rule "High Risk International"
            where amount:gt:"50000" and description:con:"SWIFT","FOREIGN":i and _raw_type:eq:"debit"
               or description:con:"CRYPTO","BITCOIN":i
            assign category_id:10 priority 1;
        '''
        rules = parse_rules(dsl_triple)
        categorizer = TransactionCategorizer(rules)

        assert (len(categorizer.find_matching_rules(tx)) > 0) == expected_match
