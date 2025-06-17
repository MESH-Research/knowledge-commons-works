import base64
import hashlib
import json
import os

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


class SecureParamEncoder:
    """
    Encrypt and encode data for URL transmission
    """

    def __init__(self, shared_secret: str):
        # Derive a 32-byte key from any length secret
        self.key = hashlib.sha256(shared_secret.encode()).digest()

    def encode(self, data: dict) -> str:
        """
        Encrypt and encode data
        """
        json_data = json.dumps(data).encode()

        # Generate random IV (init vector)
        iv = os.urandom(16)

        # Pad data to block size
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(json_data) + padder.finalize()

        # Encrypt
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        encrypted = encryptor.update(padded_data) + encryptor.finalize()

        # Combine IV + encrypted data
        result = iv + encrypted
        return base64.urlsafe_b64encode(result).decode()

    def decode(self, encrypted_param: str) -> dict:
        """
        Decrypt and decode data
        """
        data = base64.urlsafe_b64decode(encrypted_param.encode())

        # Extract IV and encrypted data
        iv = data[:16]
        encrypted = data[16:]

        # Decrypt
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(encrypted) + decryptor.finalize()

        # Remove padding
        unpadder = padding.PKCS7(128).unpadder()
        json_data = unpadder.update(padded_data) + unpadder.finalize()

        return json.loads(json_data.decode())


def diff_between_nested_dicts(original, update):
    """Return the difference between two nested dictionaries.

    At present doesn't distinguish between additions and removals
    from lists
    """  # noqa
    diff = {}
    if not original:
        return update
    else:
        for key, value in update.items():
            if isinstance(value, dict):
                diff[key] = diff_between_nested_dicts(
                    original.get(key, {}), value
                )
            elif isinstance(value, list):
                diff[key] = [
                    i for i in value if i not in original.get(key, [])
                ] + [x for x in original.get(key, []) if x not in value]
            else:
                if original.get(key) != value:
                    diff[key] = value
        diff = {k: v for k, v in diff.items() if v}
        return diff
