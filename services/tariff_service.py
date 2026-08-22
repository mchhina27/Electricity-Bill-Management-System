from database.connections import create_connection


# =========================================
# Get All Tariffs
# =========================================

def get_all_tariffs():

    connection = create_connection()

    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            tariff_id,
            connection_type,
            min_units,
            max_units,
            rate_per_unit
        FROM tariffs
        ORDER BY connection_type, min_units
    """

    try:
        cursor.execute(query)
        return cursor.fetchall()

    except Exception as e:
        print("Error fetching tariffs:", e)
        return []

    finally:
        cursor.close()
        connection.close()


# =========================================
# Add Tariff
# =========================================

def add_tariff(
    connection_type,
    min_units,
    max_units,
    rate_per_unit
):

    connection = create_connection()

    if connection is None:
        return False

    cursor = connection.cursor()

    query = """
        INSERT INTO tariffs (
            connection_type,
            min_units,
            max_units,
            rate_per_unit
        )
        VALUES (%s, %s, %s, %s)
    """

    values = (
        connection_type,
        min_units,
        max_units,
        rate_per_unit
    )

    try:
        cursor.execute(query, values)
        connection.commit()

        return True

    except Exception as e:
        print("Error adding tariff:", e)
        connection.rollback()

        return False

    finally:
        cursor.close()
        connection.close()


# =========================================
# Update Tariff
# =========================================

def update_tariff(
    tariff_id,
    connection_type,
    min_units,
    max_units,
    rate_per_unit
):

    connection = create_connection()

    if connection is None:
        return False

    cursor = connection.cursor()

    query = """
        UPDATE tariffs
        SET
            connection_type = %s,
            min_units = %s,
            max_units = %s,
            rate_per_unit = %s
        WHERE tariff_id = %s
    """

    values = (
        connection_type,
        min_units,
        max_units,
        rate_per_unit,
        tariff_id
    )

    try:
        cursor.execute(query, values)
        connection.commit()

        return True

    except Exception as e:
        print("Error updating tariff:", e)
        connection.rollback()

        return False

    finally:
        cursor.close()
        connection.close()


# =========================================
# Delete Tariff
# =========================================

def delete_tariff(tariff_id):

    connection = create_connection()

    if connection is None:
        return False

    cursor = connection.cursor()

    query = """
        DELETE FROM tariffs
        WHERE tariff_id = %s
    """

    try:
        cursor.execute(query, (tariff_id,))
        connection.commit()

        return True

    except Exception as e:
        print("Error deleting tariff:", e)
        connection.rollback()

        return False

    finally:
        cursor.close()
        connection.close()