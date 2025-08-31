import pandas as pd
import mysql.connector
from mysql.connector import Error

def load_claims(csv_file):
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',  # Replace with your MySQL password
            database='food_wastage_db'
        )
        cursor = conn.cursor()

        df = pd.read_csv(csv_file)

        # Let pandas infer the datetime format because format is inconsistent or missing seconds
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce').dt.strftime('%Y-%m-%d %H:%M:%S')

        # Check for any rows with failed conversion (NaT)
        if df['Timestamp'].isnull().any():
            print("Warning: Some timestamps couldn't be parsed and were set to NaT.")

        cols = ",".join(df.columns)
        placeholders = ",".join(['%s'] * len(df.columns))
        sql = f"INSERT INTO Claims ({cols}) VALUES ({placeholders})"

        for i, row in df.iterrows():
            cursor.execute(sql, tuple(row))

        conn.commit()
        print(f"Loaded {len(df)} records into Claims table successfully.")

    except Error as e:
        print("Error:", e)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Call the function with your CSV filename
load_claims('claims_data.csv')
