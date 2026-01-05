"""
Docstring for app.tasks.bank_statment_upload

> source venv/bin/activate
> source .env

> python app/tasks/bank_statement_upload.py --input files/union1_unlocked.pdf  --from_email noreplyunionbankofindia@unionbankofindia.bank.in --to_email nishant7.ng@gmail.com

"""
import logging

from celery import shared_task

from app.core.database import fetch_all, fetch_one
from app.model_actions.bank_account import get_or_create_bank_account
from app.model_actions.transactions import bulk_insert_transactions
from app.pdf_normalizer.parser import parse_statement
from app.pdf_normalizer.utils import get_bank_from_email
from app.rule_engine.evaluator import TransactionCategorizer
from app.rule_engine.parser import parse

logger = logging.getLogger("app")


@shared_task(
    bind=True,
    name="app.tasks.bank_statement_upload.process_bank_pdf",
    queue="statment_parser",
)
def process_bank_pdf(self, file_path: str, from_email: str, to_email: str):
    """
    Parse bank statement PDF, apply rules, and insert transactions.
    """

    # -------------------------------------------------
    # Step 1: Detect bank & parse PDF
    # -------------------------------------------------
    bank_name = get_bank_from_email(email=from_email)
    result = parse_statement(pdf_path=file_path, bank_name=bank_name)

    # -------------------------------------------------
    # Step 2: Fetch user
    # -------------------------------------------------
    user_obj = fetch_one(
        query="SELECT id FROM ss_users WHERE email = %s AND is_active = true",
        params=(to_email,),
    )
    logger.debug(user_obj)

    # -------------------------------------------------
    # Step 3: Fetch active rules (no bank filter yet)
    # -------------------------------------------------
    dsl_rules = fetch_all(
        "SELECT id, dsl_text FROM ss_categorization_rules WHERE user_id = %s and is_active=true",
        (user_obj["id"],)
    )
    logger.debug("Total %s rules fetched for user", len(dsl_rules))

    rules = []
    for data in dsl_rules:
        try:
            rules.append(parse(data["dsl_text"]))
        except Exception:
            logger.exception("Failed to parse rule = %s", data)

    # -------------------------------------------------
    # Step 4: Create / get bank account
    # -------------------------------------------------
    account_details, is_success = get_or_create_bank_account(
        user_id=user_obj["id"],
        number=result["account_details"].get("number"),
        ifsc_code=result["account_details"].get("ifsc_code"),
        account_type=result["account_details"].get("type"),
    )

    if not is_success:
        raise Exception("Could not find account details to link transactions")

    bank_account_id = account_details["id"]

    # -------------------------------------------------
    # Step 5: Apply bank-specific rule filtering (in-memory)
    # -------------------------------------------------
    filtered_rules = []
    for rule_row, rule_obj in zip(dsl_rules, rules):
        if rule_row.get("bank_id") in (None, bank_account_id):
            filtered_rules.append(rule_obj)

    categorizer = TransactionCategorizer(filtered_rules)

    # for transaction in result['transactions']:
    #     matching = categorizer.find_matching_rules(transaction)
    #     for rule in matching:
    #         logger.debug(f"  - {rule.name} (priority: {rule.priority})")

    # -------------------------------------------------
    # Step 6: Apply rules ONLY on parsed PDF transactions
    # -------------------------------------------------
    applied_rule_tx = categorizer.categorize_batch(result["transactions"])
    # logger.debug(f'Total TX {len(applied_rule_tx)} after applying rules: {applied_rule_tx}')

    # -------------------------------------------------
    # Step 7: Attach user & bank account to transactions
    # -------------------------------------------------
    for txn in applied_rule_tx:
        txn["user_id"] = user_obj["id"]
        txn["bank_account_id"] = bank_account_id

    # -------------------------------------------------
    # Step 8: Insert transactions
    # -------------------------------------------------
    stats = bulk_insert_transactions(transactions=applied_rule_tx)
    logger.info("Bulk insert stats = %s", stats)

    result["transactions"] = applied_rule_tx
    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Process bank statement PDF")
    parser.add_argument("--input", required=True, help="Input PDF file path")
    parser.add_argument("--from_email", required=True, help="Email sender")
    parser.add_argument("--to_email", required=True, help="Email receiver")

    args = parser.parse_args()

    output = process_bank_pdf( file_path=args.input,from_email=args.from_email,to_email=args.to_email,)
    
