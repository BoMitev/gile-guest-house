import mysql.connector

# Replace these values with your database configuration
db_config = {
    'host': 'localhost',
    'user': 'pelbg_admin',
    'password': 'ocOlK~}wRq(D',
    'database': 'pelbg_gile',
    'port': 3306,
}

try:
    # Establish a connection to the MySQL server
    connection = mysql.connector.connect(**db_config)

    # Check if the connection is successful
    if connection.is_connected():
        print("Connected to MySQL database!")

except mysql.connector.Error as err:
    print(f"Error: {err}")

finally:
    # Close the database connection
    if 'connection' in locals() and connection.is_connected():
        connection.close()
        print("Connection closed.")
