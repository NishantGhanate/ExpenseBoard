import re
import pdfplumber

from app.common.enums import AccountType
from app.pdf_normalizer.parsers.base_parser import BankStatementParser
from app.pdf_normalizer.parsers.base_parsing_rules import DateAmountRule
from app.pdf_normalizer.utils import account_details_dict, ss_transactions_template
from app.pdf_normalizer.values_extract import (
    determine_transaction_type,
    extract_entity_name,
    extract_payment_method,
    parse_amount,
    parse_date,
)


class KotakBankParser(BankStatementParser):
    rules = [DateAmountRule()]
    bank_name = "KOTAK"

    def detect(self, text: str) -> bool:
        self._is_kotak = "kotak mahindra bank" in text.lower() or "kkbk" in text.lower()
        return self._is_kotak


    def parse_account_details(self, text: str):
        result = account_details_dict()
        text_u = text.upper()

        acc = re.search(r"ACCOUNT\s+NO\.?\s*(\d{9,18})", text_u)
        if acc:
            result["number"] = acc.group(1)

        ifsc = re.search(r"\bKKBK0[A-Z0-9]{6}\b", text_u)
        if ifsc:
            result["ifsc_code"] = ifsc.group(0)

        acc_type = re.search(r"ACCOUNT\s+TYPE\s+(SAVINGS|CURRENT)", text_u)
        if acc_type:
            at = AccountType.from_raw(acc_type.group(1))
            result["type"] = at.value if at else None

        return result

    

    def parse_rows(self, rows):
        import pdfplumber

        txns = []

        with pdfplumber.open(self.pdf_path) as pdf:
            for page in pdf.pages:
                for table in page.find_tables():
                    data = table.extract()
                    if not data:
                        continue

                    for row in data:
                        if not row or len(row) < 7:
                            continue

                        row = [c.replace("\n", " ").strip() if c else "" for c in row]

                        # Skip headers / opening balance
                        if "OPENING BALANCE" in row[2].upper():
                            continue

                        # Kotak date: 14 Dec 2025
                        if not re.match(r"\d{1,2}\s+[A-Za-z]{3}\s+\d{4}", row[1]):
                            continue

                        txn = ss_transactions_template()

                        txn["transaction_date"] = parse_date(row[1])
                        txn["description"] = row[2]

                        if txn["description"].upper().startswith("INT.PD"):
                            txn["payment_method"] = "INTEREST"
                        else:
                            txn["payment_method"] = extract_payment_method(txn["description"])


                        txn["reference_id"] = row[3]

                        debit = row[4]
                        credit = row[5]

                        txn["amount"] = parse_amount(credit or debit)
                        txn["type"] = "credit" if credit else "debit"


                        txn["entity_name"] = extract_entity_name(txn["description"])
                        txn["payment_method"] = extract_payment_method(txn["description"])

                        txns.append(txn)

        return txns





