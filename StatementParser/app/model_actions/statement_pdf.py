import argparse
import logging
import re
import sys

from app.common.encryption import decrypt_password, encrypt_password
from app.core.database import get_cursor

logger = logging.getLogger("app")

def create_or_update_bank_pdf(
    user_id: int,
    sender_email: str,
    filename: str,
    pdf_password: str,
    cur,
    is_active: bool = True
) -> dict:
    """
    Create or update bank PDF password rule.
    Returns inserted/updated row.
    """

    encrypted_password = encrypt_password(pdf_password)

    try:

        cur.execute(
            """
            INSERT INTO ss_statement_pdfs (
                user_id,
                sender_email,
                filename,
                encrypted_password,
                is_active
            )
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (user_id, sender_email, filename)
            DO UPDATE SET
                encrypted_password = EXCLUDED.encrypted_password,
                is_active = EXCLUDED.is_active,
                updated_at = NOW()
            RETURNING *
            """,
            (
                user_id,
                sender_email,
                filename,
                encrypted_password,
                is_active
            )
        )

        row = cur.fetchone()
        logger.debug("Bank PDF rule created/updated")
        return dict(row)

    except Exception as ex:
        logger.exception("Failed to create/update bank PDF rule")
        raise ex

def get_statement_pdf_password(
    user_id: int,
    sender_email: str,
    filename: str,
    cur = None
) -> dict | None:

    # Internal logic to keep things clean
    def _logic(cursor):
        suffix = filename[-8:] if filename else ""
        file_pattern = rf"{re.escape(suffix)}$"

        cursor.execute(
            """
            SELECT encrypted_password
            FROM ss_statement_pdfs
            WHERE user_id = %s
              AND sender_email = %s
              AND filename ~ %s
              AND is_active = TRUE
            LIMIT 1
            """,
            (user_id, sender_email, file_pattern)
        )

        row = cursor.fetchone()
        if not row:
            return None

        data = dict(row)
        try:
            data["password"] = decrypt_password(data.pop("encrypted_password"))
            return data
        except Exception as dec_err:
            logger.error(f"Decryption failed: {dec_err}")
            return None

    # THE FIX: If no cursor is passed, get one.
    # If a cursor IS passed, use it directly without a 'with' block
    # so we don't accidentally close the caller's connection.
    try:
        if cur:
            return _logic(cur)
        else:
            with get_cursor() as new_cur:
                return _logic(new_cur)
    except Exception as ex:
        logger.exception(f"Error fetching password for {filename}")
        raise ex

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test bank_pdfs DB helpers")
    parser.add_argument("--user-id", type=int, required=True)
    parser.add_argument("--sender-email", required=True)
    parser.add_argument("--filename", required=True)
    parser.add_argument("--password", required=False)
    parser.add_argument("--action", choices=["insert", "get"], required=True)

    args = parser.parse_args()

    try:
        # Wrap everything in one cursor context
        with get_cursor() as cur:
            if args.action == "get":
                row = get_statement_pdf_password(
                    user_id=args.user_id,
                    sender_email=args.sender_email,
                    filename=args.filename,
                    cur=cur
                )
                print(f"\n--- Result ---\n{row}\n--------------")
    except Exception as e:
        print(f"Execution Error: {e}")

