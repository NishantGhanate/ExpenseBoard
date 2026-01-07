"""
Docstring for StatementParser.app.common.encryption
> source .env
> python ./app/common/encryption.py
"""

from app.config.settings import settings
from cryptography.fernet import Fernet

fernet = Fernet(settings.FERNET_KEY)

def encrypt_password(plain_text: str) -> str:
    """
    Docstring for encrypt_password

    :param plain_text: Description
    :type plain_text: str
    :return: Description
    :rtype: str
    """
    return fernet.encrypt(plain_text.encode()).decode()

def decrypt_password(encrypted_text: str) -> str:
    """
    Docstring for decrypt_password

    :param encrypted_text: Description
    :type encrypted_text: str
    :return: Description
    :rtype: str
    """
    return fernet.decrypt(encrypted_text.encode()).decode()

if __name__ == '__main__':
    encrypted = encrypt_password("MyPDF@123")
    print(encrypted)

    password = decrypt_password(encrypted)
    print(password)
