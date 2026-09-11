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
# Overlap check (backend validation, not just UI)
# =========================================

def _slabs_overlap(connection_type, min_units, max_units, exclude_tariff_id=None):
    """
    Returns True if [min_units, max_units] overlaps any existing tariff
    slab for the same connection_type. Ranges are treated as inclusive,
    so 1-100 and 100-200 count as overlapping (100 belongs to both).
    """
    connection = create_connection()

    if connection is None:
        # If we can't reach the database at all, let the caller's own
        # connection attempt (a few lines later) surface that error --
        # we don't want to silently block a valid add/update here.
        return False

    cursor = connection.cursor(dictionary=True)

    try:
        query = """
            SELECT tariff_id, min_units, max_units
            FROM tariffs
            WHERE connection_type = %s
        """
        params = [connection_type]

        if exclude_tariff_id is not None:
            query += " AND tariff_id != %s"
            params.append(exclude_tariff_id)

        cursor.execute(query, tuple(params))
        existing_slabs = cursor.fetchall()

        for slab in existing_slabs:
            existing_min = float(slab["min_units"])
            existing_max = float(slab["max_units"])

            if min_units <= existing_max and max_units >= existing_min:
                return True

        return False

    except Exception as e:
        print("Error checking tariff overlap:", e)
        return False

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
    try:
        min_units_f = float(min_units)
        max_units_f = float(max_units)
        rate_f = float(rate_per_unit)
    except (TypeError, ValueError):
        return False, "Units and rate must be numeric."

    if max_units_f < min_units_f:
        return False, "Maximum units cannot be less than minimum units."

    if rate_f <= 0:
        return False, "Rate per unit must be greater than 0."

    if _slabs_overlap(connection_type, min_units_f, max_units_f):
        return False, "This unit range overlaps an existing tariff slab for this connection type."

    connection = create_connection()

    if connection is None:
        return False, "Database connection failed."

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
        min_units_f,
        max_units_f,
        rate_f
    )

    try:
        cursor.execute(query, values)
        connection.commit()

        return True, "Tariff added successfully."

    except Exception as e:
        print("Error adding tariff:", e)
        connection.rollback()

        return False, f"Database error: {e}"

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
    try:
        min_units_f = float(min_units)
        max_units_f = float(max_units)
        rate_f = float(rate_per_unit)
    except (TypeError, ValueError):
        return False, "Units and rate must be numeric."

    if max_units_f < min_units_f:
        return False, "Maximum units cannot be less than minimum units."

    if rate_f <= 0:
        return False, "Rate per unit must be greater than 0."

    if _slabs_overlap(connection_type, min_units_f, max_units_f, exclude_tariff_id=tariff_id):
        return False, "This unit range overlaps an existing tariff slab for this connection type."

    connection = create_connection()

    if connection is None:
        return False, "Database connection failed."

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
        min_units_f,
        max_units_f,
        rate_f,
        tariff_id
    )

    try:
        cursor.execute(query, values)
        connection.commit()

        return True, "Tariff updated successfully."

    except Exception as e:
        print("Error updating tariff:", e)
        connection.rollback()

        return False, f"Database error: {e}"

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
