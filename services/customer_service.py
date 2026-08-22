from database.connections import create_connection


# =========================================
# GET ALL CUSTOMERS
# =========================================

def get_all_customers():

    connection = create_connection()

    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    try:

        query = """
            SELECT *
            FROM customers
            ORDER BY customer_id DESC
        """

        cursor.execute(query)

        return cursor.fetchall()

    except Exception as e:

        print("DATABASE ERROR (get customers):", e)
        return []

    finally:

        cursor.close()
        connection.close()


# =========================================
# ADD CUSTOMER
# =========================================

def add_customer(
    first_name,
    last_name,
    email,
    phone,
    address,
    city,
    state,
    pincode,
    connection_date,
    connection_type
):

    connection = create_connection()

    if connection is None:
        return False, "Database connection failed."

    cursor = connection.cursor()

    try:

        # Check if email already exists
        cursor.execute(
            """
            SELECT customer_id
            FROM customers
            WHERE email = %s
            """,
            (email,)
        )

        existing_customer = cursor.fetchone()

        if existing_customer:
            return False, "This email is already registered."

        # Insert customer
        query = """
            INSERT INTO customers (
                first_name,
                last_name,
                email,
                phone,
                address,
                city,
                state,
                pincode,
                connection_date,
                connection_type
            )
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s
            )
        """

        values = (
            first_name,
            last_name,
            email,
            phone,
            address,
            city,
            state,
            pincode,
            connection_date,
            connection_type
        )

        cursor.execute(query, values)

        connection.commit()

        return True, "Customer added successfully."

    except Exception as e:

        connection.rollback()

        print("DATABASE ERROR (add customer):", e)

        return False, f"Database error: {e}"

    finally:

        cursor.close()
        connection.close()


# =========================================
# UPDATE CUSTOMER
# =========================================

def update_customer(
    customer_id,
    first_name,
    last_name,
    email,
    phone,
    address,
    city,
    state,
    pincode,
    connection_date,
    connection_type
):

    connection = create_connection()

    if connection is None:
        return False, "Database connection failed."

    cursor = connection.cursor()

    try:

        # Check whether another customer has same email
        cursor.execute(
            """
            SELECT customer_id
            FROM customers
            WHERE email = %s
            AND customer_id != %s
            """,
            (email, customer_id)
        )

        existing_customer = cursor.fetchone()

        if existing_customer:
            return False, "This email is already registered by another customer."

        # Update customer
        query = """
            UPDATE customers
            SET
                first_name = %s,
                last_name = %s,
                email = %s,
                phone = %s,
                address = %s,
                city = %s,
                state = %s,
                pincode = %s,
                connection_date = %s,
                connection_type = %s
            WHERE customer_id = %s
        """

        values = (
            first_name,
            last_name,
            email,
            phone,
            address,
            city,
            state,
            pincode,
            connection_date,
            connection_type,
            customer_id
        )

        cursor.execute(query, values)

        connection.commit()

        return True, "Customer updated successfully."

    except Exception as e:

        connection.rollback()

        print("DATABASE ERROR (update customer):", e)

        return False, f"Database error: {e}"

    finally:

        cursor.close()
        connection.close()


# =========================================
# DELETE CUSTOMER
# =========================================

def delete_customer(customer_id):

    connection = create_connection()

    if connection is None:
        return False, "Database connection failed."

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            DELETE FROM customers
            WHERE customer_id = %s
            """,
            (customer_id,)
        )

        connection.commit()

        if cursor.rowcount == 0:
            return False, "Customer not found."

        return True, "Customer deleted successfully."

    except Exception as e:

        connection.rollback()

        print("DATABASE ERROR (delete customer):", e)

        return False, f"Database error: {e}"

    finally:

        cursor.close()
        connection.close()


# =========================================
# GET CUSTOMER BY ID
# =========================================

def get_customer_by_id(customer_id):

    connection = create_connection()

    if connection is None:
        return None

    cursor = connection.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT *
            FROM customers
            WHERE customer_id = %s
            """,
            (customer_id,)
        )

        return cursor.fetchone()

    except Exception as e:

        print("DATABASE ERROR (get customer):", e)
        return None

    finally:

        cursor.close()
        connection.close()