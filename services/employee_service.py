"""
Minimal employee-account management (ADMIN only -- enforced by the caller/UI,
same pattern as the rest of this project's service layer).
"""

from database.connections import create_connection
from services.security import hash_password
import secrets
import string


def _generate_temp_password(length=10):
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def get_all_employees():
    connection = create_connection()

    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT user_id, username, employee_name, created_at
            FROM users
            WHERE role = 'EMPLOYEE'
            ORDER BY user_id DESC
        """)
        return cursor.fetchall()

    except Exception as e:
        print("Error fetching employees:", e)
        return []

    finally:
        cursor.close()
        connection.close()


def add_employee(username, employee_name):
    if not username or not username.strip():
        return False, "Username is required."

    connection = create_connection()

    if connection is None:
        return False, "Database connection failed."

    cursor = connection.cursor()

    try:
        cursor.execute("SELECT user_id FROM users WHERE username = %s", (username.strip(),))
        if cursor.fetchone():
            return False, "That username is already taken."

        temp_password = _generate_temp_password()

        cursor.execute("""
            INSERT INTO users (username, password_hash, role, employee_name)
            VALUES (%s, %s, 'EMPLOYEE', %s)
        """, (username.strip(), hash_password(temp_password), employee_name.strip()))

        connection.commit()

        return True, (
            f"Employee account created. Username: {username.strip()}  "
            f"Temporary Password: {temp_password} (share this once; it won't be shown again)."
        )

    except Exception as e:
        connection.rollback()
        return False, f"Database error: {e}"

    finally:
        cursor.close()
        connection.close()


def delete_employee(user_id):
    connection = create_connection()

    if connection is None:
        return False, "Database connection failed."

    cursor = connection.cursor()

    try:
        cursor.execute("DELETE FROM users WHERE user_id = %s AND role = 'EMPLOYEE'", (user_id,))
        connection.commit()
        return True, "Employee account removed."

    except Exception as e:
        connection.rollback()
        return False, f"Database error: {e}"

    finally:
        cursor.close()
        connection.close()
