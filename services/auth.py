from database.connections import create_connection


def login(username, password):
    connection = create_connection()

    if connection is None:
        return None

    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT user_id, username, role
        FROM users
        WHERE username = %s AND password = %s
    """

    cursor.execute(query, (username, password))
    user = cursor.fetchone()

    cursor.close()
    connection.close()

    return user