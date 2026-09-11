from database.connections import create_connection
from services.overdue_service import mark_overdue_bills


def get_unpaid_bills():
    mark_overdue_bills()

    connection = create_connection()

    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT *
            FROM bills
            WHERE status IN ('UNPAID', 'OVERDUE')
            ORDER BY due_date
        """)

        return cursor.fetchall()

    except Exception as e:
        print("Error fetching unpaid bills:", e)
        return []

    finally:
        cursor.close()
        connection.close()


def make_payment(
    bill_id,
    customer_name,
    amount,
    payment_method,
    transaction_id="",
    customer_id=None
):
    """
    `amount` is accepted for backward compatibility but is NOT trusted --
    the authoritative total_amount is re-read from the bills table itself,
    so a formatted display string (e.g. "₹1,234.00") accidentally passed
    in can never end up stored or charged.

    If `customer_id` is provided (customer self-service payment), the bill
    must belong to that customer or the payment is rejected -- this is the
    ownership check enforced at the service layer, not just by hiding UI.
    """
    connection = create_connection()

    if connection is None:
        return False, "Database connection failed."

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT customer_id, status, total_amount
            FROM bills
            WHERE bill_id = %s
        """, (bill_id,))
        bill = cursor.fetchone()

        if bill is None:
            return False, "Bill not found."

        if customer_id is not None and str(bill["customer_id"]) != str(customer_id):
            return False, "You are not authorized to pay this bill."

        if bill["status"] == "PAID":
            return False, "This bill has already been paid."

        authoritative_amount = bill["total_amount"]

        cursor.execute("""
            INSERT INTO payments (
                bill_id,
                customer_name,
                amount,
                payment_method,
                transaction_id,
                payment_status
            )
            VALUES (%s, %s, %s, %s, %s, 'SUCCESS')
        """, (
            bill_id,
            customer_name,
            authoritative_amount,
            payment_method,
            transaction_id
        ))

        cursor.execute("""
            UPDATE bills
            SET status = 'PAID'
            WHERE bill_id = %s
        """, (bill_id,))

        connection.commit()

        return True, "Payment successful."

    except Exception as e:
        connection.rollback()
        return False, str(e)

    finally:
        cursor.close()
        connection.close()


def get_all_payments():
    connection = create_connection()

    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT *
            FROM payments
            ORDER BY payment_date DESC
        """)

        return cursor.fetchall()

    except Exception as e:
        print("Error fetching payments:", e)
        return []

    finally:
        cursor.close()
        connection.close()
