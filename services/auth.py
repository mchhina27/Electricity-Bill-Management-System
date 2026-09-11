"""
Authentication.

users.customer_id links a CUSTOMER-role account to its row in `customers`
(NULL for ADMIN/EMPLOYEE accounts). login() returns customer_id so the UI
never has to guess it from a username -- this fixes the original bug where
CustomerDashboard was opened with a username instead of a real customer_id.

Passwords are verified against users.password_hash using
services.security.verify_password, which also transparently accepts any
leftover plaintext rows (useful right after upgrading an older database)
and upgrades them to a proper hash on successful login.
"""

from database.connections import create_connection
from services.security import verify_password, hash_password, is_legacy_plaintext


def login(username, password):
    connection = create_connection()

    if connection is None:
        return None

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT user_id, username, password_hash, role, customer_id, employee_name
            FROM users
            WHERE username = %s
        """, (username,))

        user = cursor.fetchone()

        if user is None:
            return None

        if not verify_password(password, user["password_hash"]):
            return None

        # Transparent upgrade: if this row was still plaintext, rehash it
        # now that we know the correct password, so it's never stored in
        # plaintext again.
        if is_legacy_plaintext(user["password_hash"]):
            try:
                cursor.execute(
                    "UPDATE users SET password_hash = %s WHERE user_id = %s",
                    (hash_password(password), user["user_id"])
                )
                connection.commit()
            except Exception as e:
                print("Warning: could not upgrade legacy password hash:", e)

        return {
            "user_id": user["user_id"],
            "username": user["username"],
            "role": user["role"],
            "customer_id": user["customer_id"],
            "employee_name": user["employee_name"],
        }

    except Exception as e:
        print("Error during login:", e)
        return None

    finally:
        cursor.close()
        connection.close()
