"""
Password hashing helpers.

We use hashlib.pbkdf2_hmac (Python standard library — no new dependency,
no C-extension install risk) instead of bcrypt. This keeps the project
installable everywhere while still eliminating plaintext password storage:
each password is combined with a random per-user salt and hashed with
100,000 rounds of SHA-256, which is a widely accepted, safe default.

Stored format: "pbkdf2_sha256$<iterations>$<salt_hex>$<hash_hex>"
This single string is what goes in users.password_hash.
"""

import hashlib
import hmac
import os

_ALGO = "pbkdf2_sha256"
_ITERATIONS = 100_000


def hash_password(plain_password):
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt, _ITERATIONS)
    return f"{_ALGO}${_ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(plain_password, stored_hash):
    """Returns True if plain_password matches stored_hash.

    Also transparently accepts legacy plaintext values (a stored value that
    doesn't look like one of our hash strings) so any pre-existing plaintext
    demo rows still log in -- see migrate_legacy_password() to upgrade them
    on the fly.
    """
    if not stored_hash:
        return False

    parts = stored_hash.split("$")
    if len(parts) != 4 or parts[0] != _ALGO:
        # Legacy plaintext row (pre-hashing). Compare directly.
        return hmac.compare_digest(plain_password, stored_hash)

    _, iterations, salt_hex, hash_hex = parts
    try:
        salt = bytes.fromhex(salt_hex)
        iterations = int(iterations)
    except ValueError:
        return False

    digest = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt, iterations)
    return hmac.compare_digest(digest.hex(), hash_hex)


def is_legacy_plaintext(stored_hash):
    if not stored_hash:
        return False
    parts = stored_hash.split("$")
    return not (len(parts) == 4 and parts[0] == _ALGO)
