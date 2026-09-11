"""
Overdue-bill detection and a simple, one-time late fee.

RULE (kept deliberately simple for a viva explanation):
  A bill still UNPAID after its due_date becomes OVERDUE, and a flat 2%
  late fee (of its current total_amount) is added ONCE at the moment it
  transitions from UNPAID to OVERDUE. Because the fee is only applied on
  that one transition (guarded by "WHERE status = 'UNPAID'"), calling
  mark_overdue_bills() repeatedly -- on every app start or screen load --
  never re-charges the fee a second time. A PAID bill is never touched,
  so a bill can never become OVERDUE after it has been paid.
"""

from database.connections import create_connection

LATE_FEE_RATE = 0.02  # 2% flat, applied once


def mark_overdue_bills():
    """
    Finds UNPAID bills whose due_date has passed, applies the one-time late
    fee, and flips their status to OVERDUE. Returns the number of bills
    updated. Safe to call as often as needed (idempotent).
    """
    connection = create_connection()

    if connection is None:
        return 0

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT bill_id, total_amount
            FROM bills
            WHERE status = 'UNPAID' AND due_date < CURDATE()
        """)
        overdue_rows = cursor.fetchall()

        if not overdue_rows:
            return 0

        for row in overdue_rows:
            current_total = float(row["total_amount"])
            late_fee = round(current_total * LATE_FEE_RATE, 2)
            new_total = round(current_total + late_fee, 2)

            cursor.execute("""
                UPDATE bills
                SET status = 'OVERDUE',
                    late_fee = %s,
                    total_amount = %s
                WHERE bill_id = %s AND status = 'UNPAID'
            """, (late_fee, new_total, row["bill_id"]))

        connection.commit()
        return len(overdue_rows)

    except Exception as e:
        connection.rollback()
        print("Error marking overdue bills:", e)
        return 0

    finally:
        cursor.close()
        connection.close()
