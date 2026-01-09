import copy
import re

from app.pdf_normalizer.parsers.base_parser import BankStatementParser
from app.pdf_normalizer.parsers.base_parsing_rules import DateAmountRule
from app.pdf_normalizer.utils import account_details_dict, ss_transactions_template
from app.pdf_normalizer.values_extract import (
    extract_payment_method,
    parse_amount,
    parse_date,
)
from app.common.enums import AccountType


class SBIBankParser(BankStatementParser):
    rules = [DateAmountRule()]
    bank_name = "SBI"

    # -------------------------------------------------
    # Detection
    # -------------------------------------------------
    def detect(self, text: str) -> bool:
        text = text.lower()
        return "state bank of india" in text or "sbi" in text

    # -------------------------------------------------
    # Account details
    # -------------------------------------------------
    def parse_account_details(self, text: str):
        result = account_details_dict()
        text_u = text.upper()

        acc_match = re.search(
            r"(ACCOUNT\s+NUMBER|ACCOUNT\s+NO\.?|A/C\s+NO\.?)\s*[:\-]?\s*([X\d][X\d\s\-]{5,20})",
            text_u,
        )
        if acc_match:
            result["number"] = acc_match.group(2).replace(" ", "").replace("-", "")

        masked = re.findall(r"\bX{4,}\d{3,6}\b", text)
        if masked:
            result["number"] = masked[-1]

        ifsc_match = re.search(r"\bSBIN0\d{6}\b", text_u)
        if ifsc_match:
            result["ifsc_code"] = ifsc_match.group(0)

        type_patterns = [
            r"ACCOUNT\s*TYPE\s*[:\-]?\s*(SAVINGS?|CURRENT|SALARY|NRE|NRO|FD|RD)",
            r"(SAVINGS?|CURRENT|SALARY)\s*ACCOUNT",
        ]

        for pattern in type_patterns:
            match = re.search(pattern, text_u)
            if match:
                acc_type = AccountType.from_raw(match.group(1))
                result["type"] = acc_type.value if acc_type else None
                break

        return result

    # -------------------------------------------------
    # Entity extraction
    # -------------------------------------------------
    def extract_entity_from_description(self, description: str):
        if not description:
            return None

        parts = description.split("/")
        if len(parts) >= 4:
            name = parts[3].strip()
            return name if name and not name.isdigit() else None

        return None

    # -------------------------------------------------
    # SBI cleanup
    # -------------------------------------------------
    def _sbi_post_process(self, txn: dict) -> dict:
        txn = txn.copy()
        desc = (txn.get("description") or "").upper()

        if desc.startswith("UPI/REF/"):
            txn["entity_name"] = None
            txn["payment_method"] = "UPI"

        if desc.startswith("SBIYA") or "RENEWAL" in desc:
            txn["entity_name"] = "SBI"
            txn["payment_method"] = "SERVICE_CHARGE"

        if "CASH DEPOSIT" in desc:
            txn["payment_method"] = "CASH"

        return txn

    # -------------------------------------------------
    # Amount extraction (SBI safe)
    # -------------------------------------------------
    def _extract_amount_from_row(self, row):
        raw = " ".join(str(x) for x in row if x)
        numbers = re.findall(r"\d+\.\d{2}", raw)

        if not numbers:
            return None

        # SBI tables usually end with balance
        amount = numbers[-2] if len(numbers) >= 2 else numbers[0]
        return parse_amount(amount)

    # -------------------------------------------------
    # Transaction parsing
    # -------------------------------------------------
    def parse_rows(self, rows):
        seen = set()
        unique = []

        last_amount = None
        last_type = None
        row_index = 0

        for row in rows:
            row_index += 1
            raw_row = " ".join(str(x) for x in row if x)

            date_match = re.search(r"\d{2}-\d{2}-\d{2}", raw_row)
            if not date_match:
                continue

            template = copy.deepcopy(ss_transactions_template())
            template["transaction_date"] = parse_date(date_match.group())

            description = row[1] if len(row) > 1 else raw_row
            template["description"] = description

            # ---- TYPE (UPI string is authoritative)
            if "/CR/" in description:
                template["type"] = "credit"
            elif "/DR/" in description:
                template["type"] = "debit"
            else:
                template["type"] = None

            # ---- ENTITY
            template["entity_name"] = self.extract_entity_from_description(description)

            # ---- PAYMENT METHOD
            template["payment_method"] = extract_payment_method(description)

            # ---- REFERENCE ID
            ref_match = re.search(r"UPI/(CR|DR)/(\d+)", description)
            template["reference_id"] = ref_match.group(2) if ref_match else None

            # ---- AMOUNT
            amount = self._extract_amount_from_row(row)

            if amount is not None:
                template["amount"] = amount
                last_amount = amount
                last_type = template["type"]
            else:
                # wrapped-row recovery
                template["amount"] = last_amount
                if template["type"] is None:
                    template["type"] = last_type

            # ---- SBI cleanup
            template = self._sbi_post_process(template)

            # ---- FORCE INCLUDE SYSTEM ROWS
            if template["amount"] is None:
                if template["payment_method"] in {"SERVICE_CHARGE", "CASH"}:
                    template["amount"] = "0.00"
                elif description.startswith("UPI/REF/"):
                    template["amount"] = "0.00"
                    template["type"] = "credit"
                else:
                    continue

            # ---- FINAL TYPE GUARD
            if template["type"] is None:
                template["type"] = "debit"

            # ---- SAFE DEDUP (never collapse real txns)
            key = template.get("reference_id") or f"ROW-{row_index}"
            if key in seen:
                continue

            seen.add(key)
            unique.append(template)

        return unique
