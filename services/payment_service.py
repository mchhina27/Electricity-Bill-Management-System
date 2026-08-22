from database.connections import create_connection


def get_unpaid_bills():
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
    transaction_id=""
):
    connection = create_connection()

    if connection is None:
        return False, "Database connection failed."

    cursor = connection.cursor()

    try:
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
            amount,
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