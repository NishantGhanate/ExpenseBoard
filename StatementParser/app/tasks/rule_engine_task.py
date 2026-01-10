"""
Docstring for app.tasks.bank_statment_upload


"""

import logging
from datetime import date

from app.core.database import fetch_all, fetch_one
from app.model_actions.transactions import bulk_insert_transactions
from app.rule_engine.evaluator import TransactionCategorizer
from app.rule_engine.parser import parse
from celery import shared_task

logger = logging.getLogger("app")


# @shared_task(
#     bind=True,
#     name="app.tasks.bank_statement_upload.process_bank_pdf",
#     queue="statement_parser",
# )
def run_rule_engine(user_email: str, bank_account_id: int, from_date: date, to_date: date, rules_id: int):
    """
    Run rule engine for given params.
    Except for user_email all other argumetns can be None
    """
    # call db and get user_id based on to_email from ss_users table
    user_dict = fetch_one(
        query="SELECT id FROM ss_users WHERE email = %s and is_active=true", params=(user_email,)
    )
    if not user_dict:
        raise ValueError(f"Invalid user email : {user_email}")

    # Fetch user related transactions based on filter args
    # 2. Build dynamic transaction query
    # Start with mandatory user_id filter
    query_base = "SELECT * FROM ss_transactions WHERE user_id = %s"
    query_params = [user_dict['id']]

    if bank_account_id is not None:
        query_base += " AND bank_account_id = %s"
        query_params.append(bank_account_id)

    if from_date is not None:
        query_base += " AND transaction_date >= %s"
        query_params.append(from_date)

    if to_date is not None:
        query_base += " AND transaction_date <= %s"
        query_params.append(to_date)

    # 3. Fetch transactions
    transactions = fetch_all(query=query_base, params=tuple(query_params))

    if not transactions:
        return {"status": "success", "processed": 0, "message": "No transactions found"}

    result = {}

    # 1. Initialize the query and basic parameters
    query_rules = """
        SELECT id, dsl_text
        FROM ss_categorization_rules
        WHERE user_id = %s
        AND is_active = true
    """
    params_rules = [user_dict["id"]]

    # 2. Add dynamic filter for rules_id
    if rules_id:
        query_rules += " AND id = ANY(%s)"
        params_rules.append(rules_id)

    # 3. Add dynamic filter for bank_account_id (if applicable to your rules table)
    if bank_account_id:
        query_rules += " AND (bank_account_id = %s OR bank_account_id IS NULL)"
        params_rules.append(bank_account_id)

    # 4. Execute
    dsl_rules = fetch_all(query_rules, tuple(params_rules))
    logger.debug(f"Total {len(dsl_rules)} rules fetched for {user_email}")

    rules = []
    for data in dsl_rules:
        try:
            rules.append(parse(data["dsl_text"]))
        except Exception:
            logger.exception(f"Failed to parse rule = {data}")

    categorizer = TransactionCategorizer(rules)

    applied_rule_tx = categorizer.categorize_batch(transactions)

    stats = bulk_insert_transactions(transactions=applied_rule_tx)
    logger.info(f"Bulk insert stats = {stats}")

    result['count'] = len(applied_rule_tx)
    result["transactions"] = applied_rule_tx
    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run rule engine")

    parser.add_argument("--user_email", required=True, help="email reciever")
    args = parser.parse_args()

