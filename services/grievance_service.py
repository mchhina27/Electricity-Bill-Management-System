"""
Customer grievance / appeal system.

Table: grievances (customer_id FK, optional related_bill_id FK, category,
description, status, resolution, handled_by user_id, timestamps).

Ownership rule enforced here (not just in the UI): get_grievances_for_customer
only ever returns rows for that one customer_id.
"""

from database.connections import create_connection

VALID_CATEGORIES = ["INCORRECT_BILL", "METER_READING", "PAYMENT_ISSUE", "CONNECTION_ISSUE", "OTHER"]
VALID_STATUSES = ["OPEN", "IN_PROGRESS", "RESOLVED", "REJECTED"]


def submit_grievance(customer_id, category, description, related_bill_id=None):
    if category not in VALID_CATEGORIES:
        return False, "Invalid grievance category."

    if not description or not description.strip():
        return False, "Please describe the issue."

    connection = create_connection()

    if connection is None:
        return False, "Database connection failed."

    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO grievances (
                customer_id, category, description, related_bill_id, status
            )
            VALUES (%s, %s, %s, %s, 'OPEN')
        """, (customer_id, category, description.strip(), related_bill_id))

        connection.commit()
        return True, "Grievance submitted successfully."

    except Exception as e:
        connection.rollback()
        return False, f"Database error: {e}"

    finally:
        cursor.close()
        connection.close()


def get_grievances_for_customer(customer_id):
    """Ownership is enforced here: only this customer's rows are ever returned."""
    connection = create_connection()

    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT *
            FROM grievances
            WHERE customer_id = %s
            ORDER BY grievance_id DESC
        """, (customer_id,))

        return cursor.fetchall()

    except Exception as e:
        print("Error fetching customer grievances:", e)
        return []

    finally:
        cursor.close()
        connection.close()


def get_all_grievances():
    """For admin/employee use only -- callers must enforce that role check."""
    connection = create_connection()

    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT g.*, c.first_name, c.last_name, c.email
            FROM grievances g
            JOIN customers c ON g.customer_id = c.customer_id
            ORDER BY g.grievance_id DESC
        """)

        return cursor.fetchall()

    except Exception as e:
        print("Error fetching grievances:", e)
        return []

    finally:
        cursor.close()
        connection.close()


def update_grievance_status(grievance_id, status, resolution=None):
    if status not in VALID_STATUSES:
        return False, "Invalid status."

    connection = create_connection()

    if connection is None:
        return False, "Database connection failed."

    cursor = connection.cursor()

    try:
        cursor.execute("""
            UPDATE grievances
            SET status = %s, resolution = %s
            WHERE grievance_id = %s
        """, (status, resolution, grievance_id))

        connection.commit()
        return True, "Grievance updated successfully."

    except Exception as e:
        connection.rollback()
        return False, f"Database error: {e}"

    finally:
        cursor.close()
        connection.close()
