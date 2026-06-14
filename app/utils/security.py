import hashlib
import os

def hash_password(password: str) -> str:
    """
    Hashes a password securely using PBKDF2 with SHA-256 and a random salt.
    """
    salt = os.urandom(16)
    pw_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    return f"pbkdf2_sha256$100000${salt.hex()}${pw_hash.hex()}"

def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verifies a password against a PBKDF2 hash.
    """
    try:
        parts = hashed_password.split('$')
        if len(parts) != 4 or parts[0] != 'pbkdf2_sha256':
            return False
        iterations = int(parts[1])
        salt = bytes.fromhex(parts[2])
        original_hash = bytes.fromhex(parts[3])
        new_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, iterations)
        return original_hash == new_hash
    except Exception:
        return False
