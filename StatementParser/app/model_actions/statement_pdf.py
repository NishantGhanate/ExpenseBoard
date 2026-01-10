"""
Docstring for StatementParser.app.model_actions.statement_pdf

python ./app/model_actions/statement_pdf.py \
  --action insert \
  --user-id 1 \
  --sender-email statements@hdfcbank.com \
  --filename HDFC_Statement_Jun_2025.pdf \
  --password MyPDF@123


python ./app/model_actions/statement_pdf.py \
  --action get \
  --user-id 1 \
  --sender-email statements@hdfcbank.com \
  --filename HDFC_Statement_Jun_2025.pdf

"""
import logging
import re

from app.common.encryption import decrypt_password, encrypt_password
from app.core.database import get_cursor

logger = logging.getLogger("app")





def create_or_update_bank_pdf(
    user_id: int,
    sender_email: str,
    filename: str,
    pdf_password: str,
    is_active: bool = True
) -> dict:
    """
    Create or update bank PDF password rule.
    Returns inserted/updated row.
    """

    encrypted_password = encrypt_password(pdf_password)

    try:
        with get_cursor() as cur:
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
    filename: str
) -> dict | None:
    """
    Fetch active bank PDF rule and decrypt password.
    """

    try:
        suffix = filename[-8:]
        file_pattern = rf"{re.escape(suffix)}$"

        with get_cursor() as cur:
            cur.execute(
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

            row = cur.fetchone()
            if not row:
                return None

            data = dict(row)
            data["password"] = decrypt_password(data.pop("encrypted_password"))

            logger.debug("No File found")
            return data

    except Exception as ex:
        logger.exception("Failed to fetch statment PDF ")
        raise ex


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test bank_pdfs DB helpers")

    parser.add_argument("--user-id", type=int, required=True)
    parser.add_argument("--sender-email", required=True)
    parser.add_argument("--filename", required=True)
    parser.add_argument("--password", required=False)

    parser.add_argument(
        "--action",
        choices=["insert", "get"],
        required=True,
        help="Action to perform"
    )

    args = parser.parse_args()

    if args.action == "insert":
        row = create_or_update_bank_pdf(
            user_id=args.user_id,
            sender_email=args.sender_email,
            filename=args.filename,
            pdf_password=args.password
        )
        print("Inserted / Updated:")
        print(row)

    elif args.action == "get":
        row = get_statement_pdf_password(
            user_id=args.user_id,
            sender_email=args.sender_email,
            filename=args.filename
        )
        print("Fetched:")
        print(row)
