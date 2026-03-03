import base64
import hashlib
import os

from cryptography.fernet import Fernet


def _get_encryption_key() -> bytes:
    """
    環境変数からENCRYPTION_KEYを取得し、Fernet用のキーを生成する

    Returns:
        bytes: Fernet用の32バイトキー

    Raises:
        ValueError: ENCRYPTION_KEYが設定されていない場合
    """
    key = os.environ.get("ENCRYPTION_KEY")
    if not key:
        raise ValueError("ENCRYPTION_KEY environment variable is not set")

    # SHA256でハッシュ化して32バイトキーを生成
    key_hash = hashlib.sha256(key.encode()).digest()
    return base64.urlsafe_b64encode(key_hash)


def encrypt(data: str) -> str:
    """
    文字列を暗号化する

    Args:
        data: 暗号化する文字列

    Returns:
        str: Base64エンコードされた暗号化データ

    Raises:
        ValueError: ENCRYPTION_KEYが設定されていない場合
    """
    key = _get_encryption_key()
    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(data.encode())
    return encrypted_data.decode()


def decrypt(encrypted_data: str) -> str:
    """
    暗号化された文字列を復号化する

    Args:
        encrypted_data: Base64エンコードされた暗号化データ

    Returns:
        str: 復号化された文字列

    Raises:
        ValueError: ENCRYPTION_KEYが設定されていない場合
        cryptography.fernet.InvalidToken: 復号化に失敗した場合
    """
    key = _get_encryption_key()
    fernet = Fernet(key)
    decrypted_data = fernet.decrypt(encrypted_data.encode())
    return decrypted_data.decode()
