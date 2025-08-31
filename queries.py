import streamlit as st
import pandas as pd
import mysql.connector
import matplotlib.pyplot as plt

def get_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',  # update your DB password here
        database='food_wastage_db'
    )

def run_query(query, columns):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    res = cursor.fetchall()
    df = pd.DataFrame(res, columns=columns)
    cursor.close()
    conn.close()
    return df

def queries_summary():
    st.header("Data Summary Queries")

    queries = [
        {"name": "Food Available by City",
         "sql": "SELECT Location as City, SUM(Quantity) as Total_Food_Available FROM Food_Listings GROUP BY Location ORDER BY Total_Food_Available DESC;",
         "columns": ["City", "Total Food Available"],
         "chart": "bar"},

        {"name": "Top 10 Providers by Donations",
         "sql": """
             SELECT p.Name AS Provider, SUM(f.Quantity) AS Total_Donated
             FROM Providers p
             JOIN Food_Listings f ON p.Provider_ID = f.Provider_ID
             GROUP BY p.Name
             ORDER BY Total_Donated DESC
             LIMIT 10;
         """,
         "columns": ["Provider", "Total Donated"],
         "chart": "bar"},

        {"name": "Food Type Distribution",
         "sql": "SELECT Food_Type, SUM(Quantity) AS Total FROM Food_Listings GROUP BY Food_Type ORDER BY Total DESC;",
         "columns": ["Food Type", "Total Quantity"],
         "chart": "bar"},

        {"name": "Average Quantity by Meal Type",
         "sql": "SELECT Meal_Type, AVG(Quantity) AS Avg_Quantity FROM Food_Listings GROUP BY Meal_Type;",
         "columns": ["Meal Type", "Avg Quantity"],
         "chart": "bar"},

        {"name": "Expiring in Month of September",
         "sql": "SELECT Food_ID, Food_Name, Quantity, Expiry_Date, Provider_ID, Provider_Type, Location, Food_Type, Meal_Type FROM Food_Listings WHERE MONTH(Expiry_Date) = 9;",
         "columns": ["Food_ID", "Food_Name", "Quantity", "Expiry_Date", "Provider_ID", "Provider_Type", "Location", "Food_Type", "Meal_Type"],
         "chart": None},

        {"name": "Claim Status Summary",
         "sql": "SELECT Status, COUNT(*) as NumClaims FROM Claims GROUP BY Status;",
         "columns": ["Status", "Number of Claims"],
         "chart": "pie"},

        {"name": "Near Expiry (Next 2 Days)",
         "sql": "SELECT Food_ID, Food_Name, Quantity, Expiry_Date, Provider_ID, Provider_Type, Location, Food_Type, Meal_Type FROM Food_Listings WHERE Expiry_Date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 2 DAY);",
         "columns": ["Food_ID", "Food_Name", "Quantity", "Expiry_Date", "Provider_ID", "Provider_Type", "Location", "Food_Type", "Meal_Type"],
         "chart": None},

        {"name": "Total Donated by Provider",
         "sql": "SELECT p.Name AS Provider, SUM(f.Quantity) AS Total_Donated FROM Providers p JOIN Food_Listings f ON p.Provider_ID = f.Provider_ID GROUP BY Provider;",
         "columns": ["Provider", "Total Donated"],
         "chart": "bar"},

        {"name": "Top Receivers by Claims",
         "sql": "SELECT r.Name AS Receiver, COUNT(c.Claim_ID) AS Claims_Made FROM Receivers r JOIN Claims c ON r.Receiver_ID = c.Receiver_ID GROUP BY r.Receiver_ID, r.Name ORDER BY Claims_Made DESC LIMIT 10;",
         "columns": ["Receiver", "Number of Claims"],
         "chart": "bar"},

        {"name": "Claims by Day of Week",
         "sql": "SELECT DAYNAME(Timestamp) AS Day, COUNT(*) as Claims FROM Claims GROUP BY Day ORDER BY Claims DESC;",
         "columns": ["Day", "Number of Claims"],
         "chart": "bar"},

        {"name": "Most Donated Food Items",
         "sql": "SELECT Food_Name, SUM(Quantity) AS Total_Donated FROM Food_Listings GROUP BY Food_Name ORDER BY Total_Donated DESC LIMIT 10;",
         "columns": ["Food Name", "Total Donated"],
         "chart": "bar"},

        {"name": "Provider Type Breakdown",
         "sql": "SELECT Provider_Type, SUM(Quantity) AS Total FROM Food_Listings GROUP BY Provider_Type ORDER BY Total DESC;",
         "columns": ["Provider Type", "Total Quantity"],
         "chart": "bar"},

        {"name": "Vegan-Friendly Options",
         "sql": "SELECT Food_ID, Food_Name, Quantity, Expiry_Date, Provider_ID, Provider_Type, Location, Food_Type, Meal_Type FROM Food_Listings WHERE Food_Type='Vegan';",
         "columns": ["Food_ID", "Food_Name", "Quantity", "Expiry_Date", "Provider_ID", "Provider_Type", "Location", "Food_Type", "Meal_Type"],
         "chart": None},

        {"name": "Total Active Listings",
         "sql": "SELECT COUNT(*) AS Active_Listings FROM Food_Listings WHERE Expiry_Date >= CURDATE();",
         "columns": ["Active Listings"],
         "chart": None},

        {"name": "Available by Meal Type",
         "sql": "SELECT Meal_Type, COUNT(*) AS Listings FROM Food_Listings GROUP BY Meal_Type ORDER BY Listings DESC;",
         "columns": ["Meal Type", "Listings"],
         "chart": "bar"},
    ]

    for q in queries:
     with st.expander(q["name"], expanded=False):
        df = run_query(q["sql"], q["columns"])
        st.dataframe(df)

        # Pie chart for short categorical data
        if q["chart"] == "pie" and not df.empty and len(df) <= 10 and len(df.columns) == 2:
            fig, ax = plt.subplots()
            ax.pie(df[df.columns[1]], labels=df[df.columns[0]], autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
            st.pyplot(fig)
        # Bar chart for short categorical data (optional)
        elif q["chart"] == "bar" and not df.empty and len(df) <= 10:
            st.bar_chart(df.set_index(df.columns[0]))
        # Avoid chart for long lists (like Food_ID or receiver lists)


