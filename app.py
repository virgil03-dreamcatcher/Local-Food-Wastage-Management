import streamlit as st
import mysql.connector
from mysql.connector import Error
from queries import queries_summary
import pandas as pd

# Database connection
def get_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',  # Replace with your actual password if different
        database='food_wastage_db'
    )

# Fetch providers (for internal use, not filtered in UI)
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

# Fetch food listings with filters
def fetch_food_listings(city=None, food_type=None):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT f.Food_ID, f.Food_Name, f.Quantity, f.Expiry_Date, 
               p.Name, f.Location, f.Food_Type, f.Meal_Type, p.Contact
        FROM Food_Listings f
        JOIN Providers p ON f.Provider_ID = p.Provider_ID
        WHERE 1=1
    """
    params = []
    if city:
        query += " AND f.Location = %s"
        params.append(city)
    if food_type:
        query += " AND f.Food_Type = %s"
        params.append(food_type)
    cursor.execute(query, tuple(params))
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

# Count by city (used for filter options)
def count_by_city(table):
    conn = get_connection()
    cursor = conn.cursor()
    if table == "Food_Listings":
        cursor.execute("SELECT Location AS City, COUNT(*) FROM Food_Listings GROUP BY Location ORDER BY COUNT(*) DESC")
    else:
        cursor.execute("SELECT City, COUNT(*) FROM Providers GROUP BY City ORDER BY COUNT(*) DESC")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

# CRUD Operations
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

# Main App
def main():
    st.set_page_config(page_title="Food Wastage Management", layout="wide")
    st.title("Local Food Wastage Management System")

    menu = ["View Food Listings", "Manage Providers", "Add Food Listing", "Queries Summary"]
    choice = st.sidebar.selectbox("Menu", menu, key="main_menu")

    # Queries Summary
    if choice == "Queries Summary":
        queries_summary()

    # View Food Listings
    elif choice == "View Food Listings":
        st.header("Available Food Donations")

        # Get filter options
        locations = [row[0] for row in count_by_city("Food_Listings")]
        food_type_options = ["", "Non-Vegetarian", "Vegetarian", "Vegan"]

        # Filters (Provider filter REMOVED as requested)
        city_filter = st.selectbox(
            "📍 Filter by Location (City)",
            options=[""] + sorted(locations),
            key="city_filter_select"
        )
        food_type_filter = st.selectbox(
            "🥗 Filter by Food Type",
            options=food_type_options,
            key="food_type_filter_select"
        )

        # Fetch filtered data
        data = fetch_food_listings(
            city=city_filter if city_filter else None,
            food_type=food_type_filter if food_type_filter else None
        )

        # Show results
        if data:
            df = pd.DataFrame(
                data,
                columns=[
                    "Food_ID", "Food_Name", "Quantity", "Expiry_Date",
                    "Provider", "Location", "Food_Type", "Meal_Type", "Contact"
                ]
            )
            st.dataframe(df, use_container_width=True)

            # Contact Info Section
            st.subheader("📞 Contact Provider")
            selected_food_id = st.selectbox(
                "Select a Food ID to view provider details",
                options=df["Food_ID"].tolist(),
                key="contact_provider_selectbox"
            )

            # Display provider name and contact
            provider_row = df[df["Food_ID"] == selected_food_id].iloc[0]
            st.markdown(f"""
            **Provider Name:** {provider_row['Provider']}  
            **Contact:** {provider_row['Contact']}
            """)
        else:
            st.info("No food listings found with the selected filters.")

    # Manage Providers (CRUD)
    elif choice == "Manage Providers":
        st.header("🏢 Manage Providers")

        crud_option = st.radio(
            "Choose Operation",
            ["Add Provider", "Update Provider Contact", "Delete Provider", "View Providers"],
            key="provider_crud_radio"
        )

        if crud_option == "Add Provider":
            name = st.text_input("Provider Name", key="add_provider_name")
            ptype = st.text_input("Provider Type (e.g., Restaurant, NGO)", key="add_provider_type")
            address = st.text_input("Address", key="add_provider_address")
            city = st.text_input("City", key="add_provider_city")
            contact = st.text_input("Contact", key="add_provider_contact")
            if st.button("Add Provider", key="add_provider_btn"):
                if name and ptype and city and contact:
                    insert_provider(name, ptype, address, city, contact)
                    st.success(f"✅ Provider '{name}' added successfully!")
                else:
                    st.warning("Please fill all required fields.")

        elif crud_option == "Update Provider Contact":
            provider_id = st.number_input("Provider ID", min_value=1, step=1, key="update_provider_id")
            new_contact = st.text_input("New Contact Number", key="update_provider_contact")
            if st.button("Update Contact", key="update_contact_btn"):
                update_provider_contact(provider_id, new_contact)
                st.success("📞 Contact updated successfully!")

        elif crud_option == "Delete Provider":
            provider_id = st.number_input("Provider ID to Delete", min_value=1, step=1, key="delete_provider_id")
            if st.button("Delete Provider", key="delete_provider_btn"):
                delete_provider(provider_id)
                st.success("🗑️ Provider deleted successfully!")

        elif crud_option == "View Providers":
            providers = fetch_providers()
            if providers:
                df = pd.DataFrame(providers, columns=["Provider_ID", "Name", "City", "Contact"])
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No providers found.")

    # Add Food Listing
    elif choice == "Add Food Listing":
        st.header("📦 Add New Food Listing")

        food_name = st.text_input("Food Name", key="food_name_input")
        quantity = st.number_input("Quantity (e.g., 10 meals)", min_value=1, step=1, key="quantity_input")
        expiry_date = st.date_input("Expiry Date", key="expiry_date_input")
        provider_id = st.number_input("Provider ID", min_value=1, step=1, key="provider_id_input")
        provider_type = st.text_input("Provider Type", key="provider_type_input")
        location = st.text_input("Location (City)", key="location_input")
        food_type = st.selectbox("Food Type", ["Non-Vegetarian", "Vegetarian", "Vegan"], key="food_type_input")
        meal_type = st.text_input("Meal Type (e.g., Lunch, Dinner)", key="meal_type_input")

        if st.button("Add Food Listing", key="add_food_btn"):
            add_food_listing(
                food_name=food_name,
                quantity=quantity,
                expiry_date=expiry_date.strftime("%Y-%m-%d"),
                provider_id=provider_id,
                provider_type=provider_type,
                location=location,
                food_type=food_type,
                meal_type=meal_type
            )
            st.success("✅ Food listing added successfully!")

# Run app
if __name__ == "__main__":
    main()
