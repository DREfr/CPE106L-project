import streamlit as st
import sqlite3
from datetime import datetime

def connect_db():
    return sqlite3.connect("ecotrackDB.db")

def create_user(username, password):
    with connect_db() as conn:
        cursor = conn.cursor()
        role = "user"
        try:
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
            user_id = cursor.lastrowid
            cursor.execute("INSERT INTO waste_tracking (user_id, recyclable_kg, non_recyclable_kg, current_total_kg) VALUES (?, 0, 0, 0)", (user_id,))
            cursor.execute("INSERT INTO eco_points (user_id, total_points) VALUES (?, 0)", (user_id,))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

def login(username, password):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, role, company_name FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

def user_dashboard(user_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT total_points FROM eco_points WHERE user_id = ?", (user_id,))
    points = cursor.fetchone()[0]
    cursor.execute("SELECT recyclable_kg, non_recyclable_kg FROM waste_tracking WHERE user_id = ?", (user_id,))
    waste_data = cursor.fetchone()
    cursor.execute("SELECT time_of_day, day_of_week, waste_type FROM waste_collection_schedule ORDER BY date ASC LIMIT 1")
    schedule = cursor.fetchone()
    conn.close()
    
    st.subheader("User Dashboard")
    st.write(f"EcoPoints: {points}")
    st.write(f"Recyclable Trash: {waste_data[0]} kg")
    st.write(f"Non-Recyclable Trash: {waste_data[1]} kg")
    st.write(f"Next Collection: {schedule[1]}, {schedule[0]} - {schedule[2]} Trash")

def company_dashboard(company_id, company_name):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT name, cost, stock FROM vouchers WHERE company_id = ? ORDER BY stock ASC LIMIT 1", (company_id,))
    least_voucher = cursor.fetchone()
    cursor.execute("SELECT time_of_day, waste_type FROM waste_collection_schedule WHERE company_id = ?", (company_id,))
    schedule = cursor.fetchall()
    conn.close()
    
    st.subheader(f"{company_name} Dashboard")
    st.write("Least Stocked Voucher:")
    if least_voucher:
        st.write(f"{least_voucher[0]} - Cost: {least_voucher[1]} points | Stock: {least_voucher[2]}")
    else:
        st.write("No vouchers available.")
    
    st.write("Collection Schedule:")
    for entry in schedule:
        st.write(f"{entry[0]} - {entry[1]} Trash")

def main():
    st.title("EcoTrack: Smart Waste Management")
    if "page" not in st.session_state:
        st.session_state.page = "Login"
    
    menu = ["Login", "Register"]
    if "user_id" in st.session_state:
        if st.session_state.role == "company":
            menu = ["Dashboard", "Manage Collection Schedule", "Manage Vouchers", "Logout"]
        else:
            menu = ["Dashboard", "Waste Disposal", "Eco Points", "Waste Schedule", "Waste Tracking", "Logout"]
    
    choice = st.sidebar.radio("Menu", menu, index=menu.index(st.session_state.page))
    
    if choice == "Login":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user = login(username, password)
            if user:
                user_id, role, company_name = user
                st.session_state.user_id = user_id
                st.session_state.role = role
                st.session_state.company_name = company_name
                st.session_state.page = "Dashboard"
                st.rerun()
            else:
                st.error("Invalid username or password")
    
    elif choice == "Register":
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        if st.button("Register"):
            if create_user(new_username, new_password):
                st.success("User created successfully! You can now log in.")
            else:
                st.error("Username already exists.")
    
    elif choice == "Dashboard":
        if st.session_state.role == "company":
            company_dashboard(st.session_state.user_id, st.session_state.company_name)
        else:
            user_dashboard(st.session_state.user_id)
    
    elif choice == "Logout":
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

if __name__ == "__main__":
    main()
