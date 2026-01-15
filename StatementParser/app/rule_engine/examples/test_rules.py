#!/usr/bin/env python3
"""


> source .env
> python ./app/rule_engine/test_rules.py
"""

from decimal import Decimal

from app.core.database import get_cursor
from app.rule_engine.evaluator import TransactionCategorizer
from app.rule_engine.parser import parse, parse_rules


def single_test():
    rules_dsl = '''
    rule "Type - Credit Fallback" where type:eq:"credit":i  or type_id:eq:"1" assign type_id:1 category_id:16 priority 200;
    rule "Type - Debit Fallback" where type:eq:"debit":i assign type_id:2 category_id:15 priority 200;
    '''
    rules = parse_rules(rules_dsl)


    # Test case 1.1: Both conditions match
    transcation = {
        "entity_name": "KANTI RAMULU GA",
        "amount": Decimal("75000.00"),
        "type": "credit",
        "type_id": 1
    }
    categorizer = TransactionCategorizer(rules)
    result1 = categorizer.categorize(transcation)
    print(result1)


def get_rules(curr):
    curr.execute(
        """
        SELECT dsl_text FROM ss_categorization_rules where id in (25,26)
        """
    )
    rules = curr.fetchall()
    return rules

def get_transcations(curr):

    curr.execute(
        """
        SELECT * FROM ss_transactions where type_id=1 and category_id is NULL LIMIT 50
        """
    )
    transactions = curr.fetchall()
    return transactions


def test_rules():

    with get_cursor() as curr:
        transcations = get_transcations(curr)

        dsl_rules = get_rules(curr)
        rules = []
        for r in dsl_rules:
            try:
                rules.append(parse(r["dsl_text"]))
            except Exception as e:
                print(f"RULE FAILED TO PARSE: {r}")
                print(e)

        # rules = parse_rules(rules_dsl)

        categorizer = TransactionCategorizer(rules)

        for transaction in transcations:
            matching = categorizer.find_matching_rules(transaction)
            for rule in matching:
                print(f"  - {rule.name} (priority: {rule.priority})")

            result = categorizer.categorize(transaction)
            print(result)

if __name__ == "__main__":
    test_rules()
