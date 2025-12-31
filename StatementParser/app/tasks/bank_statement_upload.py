"""
Docstring for app.tasks.bank_statment_upload

> source venv/bin/activate
> source .env

> python app/tasks/bank_statement_upload.py --input files/union1_unlocked.pdf  --from_email noreplyunionbankofindia@unionbankofindia.bank.in --to_email nishant7.ng@gmail.com

"""

import logging
from app.pdf_normalizer.parser import parse_statement
from app.pdf_normalizer.utils import get_bank_from_email
from app.core.database import fetch_one, fetch_all
from app.rule_engine.parser import parse, parse_rules
from app.rule_engine.evaluator import TransactionCategorizer, RuleEvaluator
from celery import shared_task

logger = logging.getLogger("app")

@shared_task(
    bind=True,
    name='app.tasks.bank_statement_upload.process_bank_pdf',
    queue='statment_parser'
)
def process_bank_pdf(self, file_path: str, from_email: str, to_email: str):
    """
    This function binds logics togther.
    Gets bank name,


    """
    # bank_name = get_bank_from_email(email= from_email)
    # result = parse_statement(pdf_path=file_path, bank_name= bank_name)

    # call db and get user_id based on to_email from ss_users table
    user_obj = fetch_one(
        query="SELECT id FROM ss_users WHERE email = %s and is_active=true", params=(to_email,)
    )
    print(user_obj)

    # get rules from ss_categorization_rules for given user
    dsl_rules = fetch_all(
        "SELECT id, dsl_text FROM ss_categorization_rules WHERE user_id = %s and is_active=true",
        (user_obj['id'],)
    )
    print(dsl_rules)

    rules = []
    for data in dsl_rules:
        try:
            rules.append(parse(data['dsl_text']))
        except Exception:
            logger.exception(f"Failed to parse rule = {data}")

    # Load the rules
    categorizer = TransactionCategorizer(rules)
    print(categorizer)

    matching = categorizer.find_matching_rules(result['transactions'])
    for rule in matching:
        logger.debug(f"  - {rule.name} (priority: {rule.priority})")


    result = categorizer.categorize(result['transactions'])

    return result


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Extract text")
    parser.add_argument("--input", required=True, help="Input PDF file path")
    parser.add_argument("--from_email", required=True, help="email sender")
    parser.add_argument("--to_email", required=True, help="email reciever")
    args = parser.parse_args()
    result = process_bank_pdf(file_path=args.input, from_email=args.from_email, to_email=args.to_email)
    print(result)
