"""
Docstring for app.tasks.bank_statment_upload


"""

import logging
from datetime import date

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
def run_rule_engine(
    user_email: str,
    bank_account_id: int = None,
    from_date: date = None,
    to_date: date = None,
    rules_id: list[int] = None, # Usually a list for ANY
    cur = None
):
    """
    Run rule engine for given params using a single database connection.
    """

    def _logic(cursor):
        # 1. Get User ID
        cursor.execute("SELECT id FROM ss_users WHERE email = %s AND is_active=true", (user_email,))
        user_dict = cursor.fetchone()
        if not user_dict:
            raise ValueError(f"Invalid user email: {user_email}")

        # 2. Build dynamic transaction query
        query_base = "SELECT * FROM ss_transactions WHERE user_id = %s"
        query_params = [user_dict['id']]

        if bank_account_id:
            query_base += " AND bank_account_id = %s"
            query_params.append(bank_account_id)

        if from_date:
            query_base += " AND transaction_date >= %s"
            query_params.append(from_date)

        if to_date:
            query_base += " AND transaction_date <= %s"
            query_params.append(to_date)

        cursor.execute(query_base, tuple(query_params))
        transactions = cursor.fetchall()

        if not transactions:
            return {"status": "success", "processed": 0, "message": "No transactions found"}

        # 3. Build dynamic rules query
        query_rules = """
            SELECT id, dsl_text FROM ss_categorization_rules
            WHERE user_id = %s AND is_active = true
        """
        params_rules = [user_dict["id"]]

        if rules_id:
            query_rules += " AND id = ANY(%s)"
            # Ensure rules_id is a list/tuple for the ANY operator
            params_rules.append(list(rules_id) if isinstance(rules_id, (list, set)) else [rules_id])

        if bank_account_id:
            query_rules += " AND (bank_account_id = %s OR bank_account_id IS NULL)"
            params_rules.append(bank_account_id)

        cursor.execute(query_rules, tuple(params_rules))
        dsl_rules = cursor.fetchall()
        logger.debug(f"Total {len(dsl_rules)} rules fetched for {user_email}")

        # 4. Parse Rules & Categorize
        rules = []
        for data in dsl_rules:
            try:
                rules.append(parse(data["dsl_text"]))
            except Exception:
                logger.exception(f"Failed to parse rule ID {data.get('id')}")

        categorizer = TransactionCategorizer(rules)
        applied_rule_tx = categorizer.categorize_batch(transactions)

        # 5. Bulk Insert/Update (Using same cursor)
        # Note: bulk_insert_transactions uses ON CONFLICT ON CONSTRAINT
        stats = bulk_insert_transactions(transactions=applied_rule_tx, cur=cursor, update=True)

        logger.info(f"Rule engine bulk update stats = {stats}")

        return {
            'count': len(applied_rule_tx),
            'stats': stats,
            'status': 'success'
        }

    # Execute using provided cursor or checkout a new one
    if cur:
        return _logic(cur)
    else:
        from app.core.database import get_cursor
        with get_cursor() as new_cur:
            return _logic(new_cur)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run rule engine")

    parser.add_argument("--user_email", required=True, help="email reciever")
    args = parser.parse_args()

