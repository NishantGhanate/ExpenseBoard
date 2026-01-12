
"""
Common Enums
"""

from enum import StrEnum


class FileType(StrEnum):
    """
    Based on file upload mark it csv or excel
    """

    CSV = "csv"
    EXCEL = "excel"
    PDF = "pdf"

class TranscationType(StrEnum):
    UPI = 'upi'
    IMPS = 'imps'
    NEFT = 'neft'
    ATM = 'atm'
    INTERNAL_TRANSFER = 'internal_transfer'
    CHEQUE = 'cheque'
    CASH = 'cash'


class BankName(StrEnum):
    UNION = "union"
    KOTAK = "kotak"
    SBI = "sbi"
    HDFC = "hdfc"
    ICICI = "icici"
    AXIS = "axis"
    PNB = "pnb"
    BOB = "bob"
    CANARA = "canara"
    IDBI = "idbi"
    YES = "yes"
    INDUSIND = "indusind"
    FEDERAL = "federal"


BANK_EMAIL_PATTERNS = {
    BankName.UNION: r"unionbank",
    BankName.KOTAK: r"kotak",
    BankName.SBI: r"sbi\.co\.in|@sbi\.",
    BankName.HDFC: r"hdfc",
    BankName.ICICI: r"icici",
    BankName.AXIS: r"axis",
    BankName.PNB: r"pnb|punjabnational",
    BankName.BOB: r"bankofbaroda|bob",
    BankName.CANARA: r"canara",
    BankName.IDBI: r"idbi",
    BankName.YES: r"yesbank",
    BankName.INDUSIND: r"indusind",
    BankName.FEDERAL: r"federal",
}

class TrascationType(StrEnum):
    CREDIT = 'credit'
    DEBIT = 'debit'
    SELF_TRANSFER = 'self transfer'


class AccountType(StrEnum):
    SAVINGS = "SAVINGS"
    CURRENT = "CURRENT"
    SALARY = "SALARY"
    NRE = "NRE"
    NRO = "NRO"
    FD = "FD"
    RD = "RD"

    @classmethod
    def from_raw(cls, value: str | None):
        if not value:
            return None

        raw = value.replace(" ", "").upper()

        mapping = {
            "SAVING": cls.SAVINGS,
            "SAVINGS": cls.SAVINGS,
            "CURRENT": cls.CURRENT,
            "SALARY": cls.SALARY,
            "NRE": cls.NRE,
            "NRO": cls.NRO,
            "FD": cls.FD,
            "FIXEDDEPOSIT": cls.FD,
            "RD": cls.RD,
            "RECURRING": cls.RD,
        }

        for key, enum_val in mapping.items():
            if raw.startswith(key):
                return enum_val

        return None