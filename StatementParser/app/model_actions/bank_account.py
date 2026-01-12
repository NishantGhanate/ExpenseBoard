import logging
from typing import Any

from app.core.database import get_cursor

logger = logging.getLogger("app")

def get_or_create_bank_account(
    user_id: int,
    number: str,
    ifsc_code: str = None,
    account_type: str = None,
    cur=None  # 1. Accept optional cursor
) -> tuple[dict, bool]:
    """
    Get existing bank account or create new one.
    Uses provided cursor or creates a temporary one.
    Returns (account_dict, is_success)
    """

    def _logic(cursor):
        # 2. Try to get existing
        cursor.execute(
            "SELECT * FROM ss_bank_accounts WHERE number = %s",
            (number,)
        )
        row = cursor.fetchone()

        if row:
            logger.debug(f"Bank account {number} already exists")
            return dict(row), True

        # 3.
        try:
            cursor.execute(
                """
                INSERT INTO ss_bank_accounts (user_id, number, ifsc_code, type)
                VALUES (%s, %s, %s, %s)
                RETURNING *
                """,
                (user_id, number, ifsc_code, account_type)
            )
            logger.debug(f"Bank account {number} created")
            new_row = cursor.fetchone()
            return dict(new_row), True
        except Exception:
            # Fallback: If insert fails (e.g. race condition), try fetching once more
            cursor.execute("SELECT * FROM ss_bank_accounts WHERE number = %s", (number,))
            row = cursor.fetchone()
            if row:
                return dict(row), True
            raise

    # 4. Use existing cursor or checkout a new one
    try:
        if cur:
            return _logic(cur)
        else:
            with get_cursor() as new_cur:
                return _logic(new_cur)

    except Exception as ex:
        logger.exception(f"Failed to get or create bank details for account {number}")
        # Return False for success status so the task knows it failed
        raise ex
