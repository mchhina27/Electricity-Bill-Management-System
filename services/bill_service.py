from datetime import date, timedelta
from database.connections import create_connection


def calculate_energy_charge(connection_type, units_consumed):
    connection = create_connection()

    if connection is None:
        return 0

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT min_units, max_units, rate_per_unit
            FROM tariffs
            WHERE connection_type = %s
            ORDER BY min_units
        """, (connection_type,))

        tariffs = cursor.fetchall()

        remaining_units = float(units_consumed)
        energy_charge = 0.0

        for tariff in tariffs:
            min_units = float(tariff["min_units"])
            max_units = float(tariff["max_units"])
            rate = float(tariff["rate_per_unit"])

            slab_size = max_units - min_units + 1

            if remaining_units <= 0:
                break

            units_in_slab = min(remaining_units, slab_size)

            energy_charge += units_in_slab * rate
            remaining_units -= units_in_slab

        return round(energy_charge, 2)

    except Exception as e:
        print("Error calculating energy charge:", e)
        return 0

    finally:
        cursor.close()
        connection.close()


def get_all_customers_with_meters():
    connection = create_connection()

    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                c.*,
                m.*
            FROM customers c
            JOIN meters m
                ON c.customer_id = m.customer_id
        """)

        return cursor.fetchall()

    except Exception as e:
        print("Error fetching customers and meters:", e)
        return []

    finally:
        cursor.close()
        connection.close()


def get_customer_meter_details(customer_id):
    connection = create_connection()

    if connection is None:
        return None

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                c.*,
                m.*
            FROM customers c
            JOIN meters m
                ON c.customer_id = m.customer_id
            WHERE c.customer_id = %s
        """, (customer_id,))

        return cursor.fetchone()

    except Exception as e:
        print("Error fetching meter details:", e)
        return None

    finally:
        cursor.close()
        connection.close()


def get_last_bill_reading(customer_id):
    connection = create_connection()

    if connection is None:
        return 0

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT current_reading
            FROM bills
            WHERE customer_id = %s
            ORDER BY bill_id DESC
            LIMIT 1
        """, (customer_id,))

        result = cursor.fetchone()

        if result:
            return float(result["current_reading"])

        return 0

    except Exception as e:
        print("Error getting previous reading:", e)
        return 0

    finally:
        cursor.close()
        connection.close()


def generate_bill(
    customer_id,
    customer_name,
    email,
    phone,
    address,
    connection_type,
    meter_number,
    billing_month,
    previous_reading,
    current_reading
):
    try:
        previous_reading = float(previous_reading)
        current_reading = float(current_reading)

        if current_reading < previous_reading:
            return False, "Current reading cannot be less than previous reading."

        units_consumed = current_reading - previous_reading

        energy_charge = calculate_energy_charge(
            connection_type,
            units_consumed
        )

        fixed_charge = 0.0
        tax = round(energy_charge * 0.05, 2)
        late_fee = 0.0

        total_amount = round(
            energy_charge +
            fixed_charge +
            tax +
            late_fee,
            2
        )

        due_date = date.today() + timedelta(days=15)

        connection = create_connection()

        if connection is None:
            return False, "Database connection failed."

        cursor = connection.cursor()

        query = """
            INSERT INTO bills (
                customer_id,
                customer_name,
                email,
                phone,
                address,
                connection_type,
                meter_number,
                billing_month,
                previous_reading,
                current_reading,
                units_consumed,
                energy_charge,
                fixed_charge,
                tax,
                late_fee,
                total_amount,
                due_date,
                status
            )
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s
            )
        """

        values = (
            customer_id,
            customer_name,
            email,
            phone,
            address,
            connection_type,
            meter_number,
            billing_month,
            previous_reading,
            current_reading,
            units_consumed,
            energy_charge,
            fixed_charge,
            tax,
            late_fee,
            total_amount,
            due_date,
            "UNPAID"
        )

        cursor.execute(query, values)
        connection.commit()

        cursor.close()
        connection.close()

        return True, total_amount

    except Exception as e:
        print("Error generating bill:", e)
        return False, str(e)


def get_all_bills():
    connection = create_connection()

    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT *
            FROM bills
            ORDER BY bill_id DESC
        """)

        return cursor.fetchall()

    except Exception as e:
        print("Error fetching bills:", e)
        return []

    finally:
        cursor.close()
        connection.close()


def get_customer_bills(customer_id):
    connection = create_connection()

    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT *
            FROM bills
            WHERE customer_id = %s
            ORDER BY bill_id DESC
        """, (customer_id,))

        return cursor.fetchall()

    except Exception as e:
        print("Error fetching customer bills:", e)
        return []

    finally:
        cursor.close()
        connection.close()