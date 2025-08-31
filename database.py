import mysql.connector
from mysql.connector import Error

def get_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',          
        password='root',          
        database='food_wastage_db'
    )

def add_provider(name, provider_type, address, city, contact):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = "INSERT INTO Providers (Name, Type, Address, City, Contact) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql, (name, provider_type, address, city, contact))
        conn.commit()
    except Error as e:
        print("Error:", e)
    finally:
        cursor.close()
        conn.close()

def get_providers():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT Provider_ID, Name, City FROM Providers")
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
