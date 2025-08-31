import streamlit as st
import mysql.connector
from mysql.connector import Error
from queries import queries_summary
import pandas as pd

def get_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',  # Replace with your password
        database='food_wastage_db'
    )

def fetch_providers(city=None):
    conn = get_connection()
    cursor = conn.cursor()
    if city:
        cursor.execute("SELECT Provider_ID, Name, City, Contact FROM Providers WHERE City = %s", (city,))
    else:
        cursor.execute("SELECT Provider_ID, Name, City, Contact FROM Providers")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

def fetch_food_listings(city=None, provider_name=None, food_type=None):
    conn = get_connection()
    cursor = conn.cursor()
    query = """SELECT f.Food_ID, f.Food_Name, f.Quantity, f.Expiry_Date, p.Name, f.Location, f.Food_Type, f.Meal_Type, p.Contact
               FROM Food_Listings f
               JOIN Providers p ON f.Provider_ID = p.Provider_ID
               WHERE 1=1"""
    params = []
    if city:
        query += " AND f.Location = %s"
        params.append(city)
    if provider_name:
        query += " AND p.Name = %s"
        params.append(provider_name)
    if food_type:
        query += " AND f.Food_Type = %s"
        params.append(food_type)
    cursor.execute(query, tuple(params))
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

def insert_provider(name, ptype, address, city, contact):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Providers (Name, Type, Address, City, Contact) VALUES (%s, %s, %s, %s, %s)",
        (name, ptype, address, city, contact)
    )
    conn.commit()
    cursor.close()
    conn.close()

def delete_provider(provider_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Providers WHERE Provider_ID = %s", (provider_id,))
    conn.commit()
    cursor.close()
    conn.close()

def update_provider_contact(provider_id, new_contact):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Providers SET Contact = %s WHERE Provider_ID = %s", (new_contact, provider_id))
    conn.commit()
    cursor.close()
    conn.close()

def add_food_listing(food_name, quantity, expiry_date, provider_id, provider_type, location, food_type, meal_type):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO Food_Listings (Food_Name, Quantity, Expiry_Date, Provider_ID, Provider_Type, Location, Food_Type, Meal_Type)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
        (food_name, quantity, expiry_date, provider_id, provider_type, location, food_type, meal_type)
    )
    conn.commit()
    cursor.close()
    conn.close()

def update_food_quantity(food_id, new_quantity):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Food_Listings SET Quantity = %s WHERE Food_ID = %s", (new_quantity, food_id))
    conn.commit()
    cursor.close()
    conn.close()

def delete_food(food_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Food_Listings WHERE Food_ID = %s", (food_id,))
    conn.commit()
    cursor.close()
    conn.close()

def count_by_city(table):
    conn = get_connection()
    cursor = conn.cursor()
    if table == "Food_Listings":
        cursor.execute(f"SELECT Location AS City, COUNT(*) FROM {table} GROUP BY Location ORDER BY COUNT(*) DESC")
    else:
        cursor.execute(f"SELECT City, COUNT(*) FROM {table} GROUP BY City ORDER BY COUNT(*) DESC")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

def count_food_listings_by_provider_city():
    conn = get_connection()
    cursor = conn.cursor()
    query = """
    SELECT p.City, COUNT(*)
    FROM Food_Listings f
    JOIN Providers p ON f.Provider_ID = p.Provider_ID
    GROUP BY p.City
    ORDER BY COUNT(*) DESC;
    """
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

def main():
    st.title("Local Food Wastage Management System")

    menu = ["View Food Listings", "Manage Providers", "Add Food Listing", "Queries Summary"]
    choice = st.sidebar.selectbox("Menu", menu)
    
    if choice == "Queries Summary":
        queries_summary() 

    if choice == "View Food Listings":
        st.header("Filter Food Donations")

        locations = list({row[0] for row in count_by_city("Food_Listings")})
        providers = [p[1] for p in fetch_providers()]

        city_filter = st.selectbox("Filter by Location (City)", options=[""] + sorted(locations))
        provider_filter = st.selectbox("Filter by Provider Name", options=[""] + sorted(providers))
        # Updated fixed food type filter options
        food_type_options = ["", "Non-Vegetarian", "Vegetarian", "Vegan"]
        food_type_filter = st.selectbox("Filter by Food Type", options=food_type_options)

        data = fetch_food_listings(
            city=city_filter if city_filter else None,
            provider_name=provider_filter if provider_filter else None,
            food_type=food_type_filter if food_type_filter else None
        )

        df = pd.DataFrame(data, columns=["Food_ID", "Food_Name", "Quantity", "Expiry_Date", "Provider", "Location", "Food_Type", "Meal_Type", "Contact"])
        st.dataframe(df)

        if not df.empty:
            st.subheader("Contact Info")
            selected = st.selectbox("Select Food ID to Contact Provider", df["Food_ID"].tolist())
            contact = df.loc[df["Food_ID"] == selected, "Contact"].values[0]
            st.write(f"Contact Provider: {contact}")

    elif choice == "Manage Providers":
        st.header("CRUD Operations - Providers")

        crud_option = st.radio("Choose Operation", ["Add Provider", "Update Provider Contact", "Delete Provider", "View Providers"])

        if crud_option == "Add Provider":
            name = st.text_input("Name")
            ptype = st.text_input("Type")
            address = st.text_input("Address")
            city = st.text_input("City")
            contact = st.text_input("Contact")
            if st.button("Add Provider"):
                insert_provider(name, ptype, address, city, contact)
                st.success("Provider added!")

        elif crud_option == "Update Provider Contact":
            provider_id = st.number_input("Provider ID", min_value=1, step=1)
            new_contact = st.text_input("New Contact")
            if st.button("Update Contact"):
                update_provider_contact(provider_id, new_contact)
                st.success("Contact updated!")

        elif crud_option == "Delete Provider":
            provider_id = st.number_input("Provider ID to Delete", min_value=1, step=1)
            if st.button("Delete Provider"):
                delete_provider(provider_id)
                st.success("Provider deleted!")

        elif crud_option == "View Providers":
            providers = fetch_providers()
            df = pd.DataFrame(providers, columns=["Provider_ID", "Name", "City", "Contact"])
            st.dataframe(df)

    elif choice == "Add Food Listing":
        st.header("Add Food Listing")
        food_name = st.text_input("Food Name")
        quantity = st.number_input("Quantity", min_value=1, step=1)
        expiry_date = st.date_input("Expiry Date")
        provider_id = st.number_input("Provider ID", min_value=1, step=1)
        provider_type = st.text_input("Provider Type")
        location = st.text_input("Location")
        food_type = st.selectbox("Food Type", ["Non-Vegetarian", "Vegetarian", "Vegan"])
        meal_type = st.text_input("Meal Type")

        if st.button("Add Food Listing"):
            add_food_listing(food_name, quantity, expiry_date.strftime("%Y-%m-%d"), provider_id, provider_type, location, food_type, meal_type)
            st.success("Food listing added!")


if __name__ == "__main__":
    main()
