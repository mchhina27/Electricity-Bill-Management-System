from database.connections import create_connection


# =========================================
# Get All Meters
# =========================================

def get_all_meters():

    connection = create_connection()

    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            meter_id,
            customer_id,
            meter_number,
            meter_type,
            installation_date,
            initial_reading,
            current_reading,
            meter_status
        FROM meters
        ORDER BY meter_id
    """

    try:
        cursor.execute(query)
        meters = cursor.fetchall()

        return meters

    except Exception as e:
        print("Error fetching meters:", e)
        return []

    finally:
        cursor.close()
        connection.close()


# =========================================
# Add Meter
# =========================================

def add_meter(
    customer_id,
    meter_number,
    meter_type,
    installation_date,
    initial_reading,
    current_reading,
    meter_status
):

    connection = create_connection()

    if connection is None:
        return False

    cursor = connection.cursor()

    query = """
        INSERT INTO meters (
            customer_id,
            meter_number,
            meter_type,
            installation_date,
            initial_reading,
            current_reading,
            meter_status
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        customer_id,
        meter_number,
        meter_type,
        installation_date,
        initial_reading,
        current_reading,
        meter_status
    )

    try:
        cursor.execute(query, values)
        connection.commit()

        return True

    except Exception as e:
        print("Error adding meter:", e)
        connection.rollback()

        return False

    finally:
        cursor.close()
        connection.close()


# =========================================
# Update Meter
# =========================================

def update_meter(
    meter_id,
    customer_id,
    meter_number,
    meter_type,
    installation_date,
    initial_reading,
    current_reading,
    meter_status
):

    connection = create_connection()

    if connection is None:
        return False

    cursor = connection.cursor()

    query = """
        UPDATE meters
        SET
            customer_id = %s,
            meter_number = %s,
            meter_type = %s,
            installation_date = %s,
            initial_reading = %s,
            current_reading = %s,
            meter_status = %s
        WHERE meter_id = %s
    """

    values = (
        customer_id,
        meter_number,
        meter_type,
        installation_date,
        initial_reading,
        current_reading,
        meter_status,
        meter_id
    )

    try:
        cursor.execute(query, values)
        connection.commit()

        return True

    except Exception as e:
        print("Error updating meter:", e)
        connection.rollback()

        return False

    finally:
        cursor.close()
        connection.close()


# =========================================
# Delete Meter
# =========================================

def delete_meter(meter_id):

    connection = create_connection()

    if connection is None:
        return False

    cursor = connection.cursor()

    query = """
        DELETE FROM meters
        WHERE meter_id = %s
    """

    try:
        cursor.execute(query, (meter_id,))
        connection.commit()

        return True

    except Exception as e:
        print("Error deleting meter:", e)
        connection.rollback()

        return False

    finally:
        cursor.close()
        connection.close()