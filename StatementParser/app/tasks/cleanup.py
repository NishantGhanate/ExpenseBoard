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

from celery import shared_task

logger = logging.getLogger("app")


@shared_task(
    bind=True,
    name="app.tasks.cleanup.cleanup_resources",
    queue="statement_parser",
)
def cleanup_resources(self):
    try:
        pass
    except Exception:
        logger.exception("Clean up failed")
