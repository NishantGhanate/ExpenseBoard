"""
Docstring for app.tasks.bank_statment_upload

> source venv/bin/activate
> source .env

> python app/tasks/bank_statement_upload.py --file_path files/sbi.pdf   --from_email noreply@sbi.com   --to_email nishant7.ng@gmail.com
> python app/tasks/bank_statement_upload.py --filename kotak.pdf --file_path files/kotak.pdf  --from_email BankStatements@kotak.bank.in  --to_email nishant7.ng@gmail.com

> python app/tasks/bank_statement_upload.py --file_path files/union1_unlocked.pdf  --from_email noreplyunionbankofindia@unionbankofindia.bank.in --to_email nishant7.ng@gmail.com
> python app/tasks/bank_statement_upload.py --file_path files/kotak.pdf   --from_email noreply@kotak.com   --to_email nishant7.ng@gmail.com

"""

import logging

from app.core.database import get_cursor
from app.model_actions.bank_account import get_or_create_bank_account
from app.model_actions.statement_pdf import get_statement_pdf_password
from app.model_actions.transactions import bulk_insert_transactions
from app.pdf_normalizer.parser import parse_statement
from app.pdf_normalizer.pdf_unlock import is_pdf_password_protected, unlock_pdf
from app.pdf_normalizer.utils import get_bank_from_email
from app.rule_engine.evaluator import TransactionCategorizer
from app.rule_engine.parser import parse
from celery import shared_task

logger = logging.getLogger("app")


@shared_task(bind=True, name="app.tasks.bank_statement_upload.process_bank_pdf", queue="statement_parser")
def process_bank_pdf(self, filename: str, file_path: str, from_email: str, to_email: str):

    # OPEN ONE CONNECTION FOR THE ENTIRE TASK
    result = {}

    with get_cursor() as cur:

        # 1. Fetch User
        cur.execute("SELECT id FROM ss_users WHERE email = %s AND is_active=true", (to_email,))
        user_dict = cur.fetchone()
        if not user_dict:
            raise Exception(f"User {to_email} not found")

        # 2. Handle Password
        if is_pdf_password_protected(file_path=file_path):
            # Ensure get_statement_pdf_password is updated to accept 'cur'
            password_dict = get_statement_pdf_password(
                user_id=user_dict['id'], sender_email=from_email, filename=filename, cur=cur
            )
            if not password_dict:
                raise Exception("Password not found")
            file_path = unlock_pdf(file_path=file_path, password=password_dict['password'])

        # 3. Parse (CPU Bound)
        bank_name = get_bank_from_email(email=from_email)
        result = parse_statement(pdf_path=file_path, bank_name=bank_name)

        # 4. Get/Create Account (Pass cur)
        account_details, is_success = get_or_create_bank_account(
            user_id=user_dict["id"],
            number=result["account_details"].get("number"),
            ifsc_code=result["account_details"].get("ifsc_code"),
            cur=cur
        )

        # 5. Fetch Rules (ANY syntax for safety)
        cur.execute("""
            SELECT id, dsl_text FROM ss_categorization_rules
            WHERE user_id = %s AND is_active = true
            AND (bank_account_id IS NULL OR bank_account_id = %s)
        """, (user_dict["id"], account_details["id"]))
        dsl_rules = cur.fetchall()

        # 6. Categorize (In-memory)
        categorizer = TransactionCategorizer([parse(r["dsl_text"]) for r in dsl_rules])
        applied_rule_tx = categorizer.categorize_batch(result["transactions"])

        for tx in applied_rule_tx:
            tx.update({"user_id": user_dict["id"], "bank_account_id": account_details["id"]})

        # 7. Bulk Insert (Using the same open cursor)
        stats = bulk_insert_transactions(transactions=applied_rule_tx, cur=cur)

        logger.info(f"Task completed. Stats: {stats}")

    result['count'] = len(applied_rule_tx)
    result["transactions"] = applied_rule_tx
    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Extract text")
    parser.add_argument("--filename", required=False, help="Input PDF file name", default=None)
    parser.add_argument("--file_path", required=True, help="Input PDF file path")
    parser.add_argument("--from_email", required=True, help="email sender")
    parser.add_argument("--to_email", required=True, help="email reciever")
    args = parser.parse_args()

    result = process_bank_pdf(
        filename=args.filename,
        file_path=args.file_path,
        from_email=args.from_email,
        to_email=args.to_email,
    )
