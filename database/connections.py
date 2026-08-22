import mysql.connector
from mysql.connector import Error


def create_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="270906",
            database="electricity_billing"
        )

        if connection.is_connected():
            print("Successfully connected to MySQL!")
            return connection

    except Error as e:
        print("Error connecting to MySQL:", e)

    return None


if __name__ == "__main__":
    connection = create_connection()

    if connection:
        connection.close()
        print("MySQL connection closed.")