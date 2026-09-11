from database.connections import create_connection
from services.overdue_service import mark_overdue_bills


def get_dashboard_statistics():

    mark_overdue_bills()

    connection = create_connection()

    if connection is None:
        return {}

    cursor = connection.cursor(dictionary=True)

    try:

        cursor.execute(
            "SELECT COUNT(*) AS total FROM customers"
        )
        total_customers = cursor.fetchone()["total"]

        cursor.execute(
            "SELECT COUNT(*) AS total FROM meters"
        )
        total_meters = cursor.fetchone()["total"]

        cursor.execute(
            "SELECT COUNT(*) AS total FROM bills"
        )
        total_bills = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COALESCE(SUM(total_amount), 0) AS total
            FROM bills
        """)
        total_billed = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0) AS total
            FROM payments
            WHERE payment_status = 'SUCCESS'
        """)
        total_collected = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM bills
            WHERE status IN ('UNPAID', 'OVERDUE')
        """)
        unpaid_bills = cursor.fetchone()["total"]

        return {
            "total_customers": total_customers,
            "total_meters": total_meters,
            "total_bills": total_bills,
            "total_billed": total_billed,
            "total_collected": total_collected,
            "unpaid_bills": unpaid_bills
        }

    except Exception as e:
        print("Report error:", e)
        return {}

    finally:
        cursor.close()
        connection.close()