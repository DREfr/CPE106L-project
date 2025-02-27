import streamlit as st
import sqlite3

# Function to connect to the database
def connect_db():
    return sqlite3.connect("ecotrackDB.db")

# Function to handle user login
def login(username, password):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    if user and user[2] == password:
        return user[0]  # Return user ID
    else:
        return None

# Function to handle user registration
def create_user(username, password):
    conn = connect_db()
    cursor = conn.cursor()
    role = "user"  # Set role to "user" by default
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
        user_id = cursor.lastrowid
        cursor.execute("INSERT INTO waste_tracking (user_id, recyclable_kg, non_recyclable_kg, current_total_kg) VALUES (?, 0, 0, 0)", (user_id,))
        cursor.execute("INSERT INTO eco_points (user_id, total_points) VALUES (?, 0)", (user_id,))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

# Function to show waste collection schedule
def show_waste_collection(user_id):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT time_of_day, day_of_week, day, month, waste_type FROM waste_collection_schedule ORDER BY date ASC LIMIT 5")
        schedules = cursor.fetchall()
        
        if schedules:
            st.write("\n===== Upcoming Waste Collection =====")
            for s in schedules:
                st.write(f" - {s[1]}, {s[2]} {s[3]} ({s[0]}): {s[4]}")
        else:
            st.write("No upcoming collection dates available.")

# Function to show waste tracking information
def show_waste_tracking(user_id):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT recyclable_kg, non_recyclable_kg, current_total_kg FROM waste_tracking WHERE user_id = ?", (user_id,))
        tracking = cursor.fetchone()
        
        if tracking:
            st.write("\n===== Waste Tracking Information =====")
            st.write(f" - Recyclable Trash: {tracking[0]} kg")
            st.write(f" - Non-Recyclable Trash: {tracking[1]} kg")
            st.write(f" - Current Total Trash: {tracking[2]} kg")
        else:
            st.write("No waste tracking data available.")

# Function to show eco points
def show_eco_points(user_id):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT total_points FROM eco_points WHERE user_id = ?", (user_id,))
        points = cursor.fetchone()
        st.write(f"Your current EcoPoints: {points[0]}" if points else "No EcoPoints found.")

# Function to show owned vouchers
def show_owned_vouchers(user_id):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT v.name, rv.date_redeemed, rv.used 
            FROM redeemed_vouchers rv
            JOIN vouchers v ON rv.voucher_id = v.id
            WHERE rv.user_id = ?
        """, (user_id,))
        vouchers = cursor.fetchall()
        
        if vouchers:
            st.write("\nYour Owned Vouchers:")
            for v in vouchers:
                status = "Used" if v[2] else "Not Used"
                st.write(f" - {v[0]} (Redeemed on: {v[1]}) [{status}]")
        else:
            st.write("You have no vouchers.")

# Function to show available vouchers
def show_available_vouchers():
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, cost, stock FROM vouchers WHERE stock > 0")
        vouchers = cursor.fetchall()
        
        if vouchers:
            st.write("\nAvailable Vouchers:")
            for v in vouchers:
                st.write(f"{v[0]}. {v[1]} - {v[2]} points (Stock: {v[3]})")
        else:
            st.write("No vouchers available.")

# Function to purchase a voucher
def purchase_voucher(user_id):
    show_eco_points(user_id)
    show_available_vouchers()
    
    voucher_id = st.text_input("Enter the voucher ID to purchase:")
    confirm = st.button("Confirm Purchase")
    if confirm:
        with connect_db() as conn:
            cursor = conn.cursor()
            
            # Get voucher cost and stock
            cursor.execute("SELECT cost, stock FROM vouchers WHERE id = ? AND stock > 0", (voucher_id,))
            voucher = cursor.fetchone()
            if not voucher:
                st.write("Invalid voucher ID or out of stock.")
                return
            
            cost, stock = voucher
            
            # Check user EcoPoints balance
            cursor.execute("SELECT total_points FROM eco_points WHERE user_id = ?", (user_id,))
            points = cursor.fetchone()[0]
            
            if points < cost:
                st.write("Insufficient EcoPoints.")
                return
            
            # Deduct EcoPoints, update stock, and insert redemption record
            cursor.execute("UPDATE eco_points SET total_points = total_points - ? WHERE user_id = ?", (cost, user_id))
            cursor.execute("UPDATE vouchers SET stock = stock - 1 WHERE id = ?", (voucher_id,))
            cursor.execute("INSERT INTO redeemed_vouchers (user_id, voucher_id, used) VALUES (?, ?, 0)", (user_id, voucher_id))
            conn.commit()
            
            st.write("Voucher redeemed successfully!")

# Function to display the eco points menu
def eco_points_menu(user_id):
    st.write("\n===== Eco Points System =====")
    choice = st.selectbox("Choose an option:", ["Show Total EcoPoints", "Show Owned Vouchers", "Show Available Vouchers", "Purchase Voucher", "Exit to Menu"])
    
    if choice == "Show Total EcoPoints":
        show_eco_points(user_id)
    elif choice == "Show Owned Vouchers":
        show_owned_vouchers(user_id)
    elif choice == "Show Available Vouchers":
        show_available_vouchers()
    elif choice == "Purchase Voucher":
        purchase_voucher(user_id)
    elif choice == "Exit to Menu":
        st.write("Returning to menu...")

# Function to display the user dashboard
def user_dashboard(user_id):
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    cursor.execute("SELECT total_points FROM eco_points WHERE user_id = ?", (user_id,))
    ecopoints = cursor.fetchone()
    cursor.execute("SELECT recyclable_kg, non_recyclable_kg FROM waste_tracking WHERE user_id = ?", (user_id,))
    waste_data = cursor.fetchone()
    cursor.execute("SELECT time_of_day, day_of_week, waste_type FROM waste_collection_schedule ORDER BY date ASC LIMIT 1")
    schedule = cursor.fetchone()
    
    conn.close()
    
    if user and waste_data and schedule:
        st.write(f"\n===== Dashboard for {user[0]} =====")
        st.write(f" - EcoPoints: {ecopoints[0]}")
        st.write(f" - Recyclable Trash: {waste_data[0]} kg")
        st.write(f" - Non-Recyclable Trash: {waste_data[1]} kg")
        st.write(f" - Next Trash Collection Details: {schedule[1]}, {schedule[0]}. Please take out {schedule[2]} trash.")
    else:
        st.write("Error: Missing user or waste tracking data.")
    
    user_options(user_id)

# Function to handle waste disposal
def waste_disposal(user_id):
    st.write("\nWaste Disposal:")
    choice = st.selectbox("Choose an option:", ["Recyclable", "Non-Recyclable", "I Don't Know", "Exit to Menu"])

    if choice == "Exit to Menu":
        st.write("Returning to menu...")
        return

    with connect_db() as conn:
        cursor = conn.cursor()

        recyclable = 1 if choice == "Recyclable" else 0 if choice == "Non-Recyclable" else None
        weight_kg = st.number_input("Enter weight (kg):", min_value=0.0, format="%.2f")

        if recyclable is None:
            user_input = st.text_input("Enter the type of trash:")
            cursor.execute("SELECT recyclable FROM recyclable_materials WHERE ? LIKE '%' || material || '%'", (user_input,))
            result = cursor.fetchone()
            if result is not None:
                recyclable = result[0]
            else:
                st.write("Data unavailable. Please check manually.")
                return  # Returns to the waste disposal menu

        column = "recyclable_kg" if recyclable else "non_recyclable_kg"
        cursor.execute(f"UPDATE waste_tracking SET {column} = {column} + ?, current_total_kg = current_total_kg + ? WHERE user_id = ?", (weight_kg, weight_kg, user_id))
        if recyclable:
            cursor.execute("UPDATE eco_points SET total_points = total_points + ? WHERE user_id = ?", (int(weight_kg), user_id))
            st.write(f"You earned {int(weight_kg)} EcoPoints!")
        conn.commit()
        st.write("Waste recorded successfully.")

# Function to display user options
def user_options(user_id):
    st.title("Menu")
    choice = st.selectbox("Choose an option:", ["Dashboard", "Waste Disposal", "Eco Points Menu", "Waste Collection Schedule", "Waste Tracking", "Logout"])
    
    if choice == "Dashboard":
        user_dashboard(user_id)
    elif choice == "Waste Disposal":
        waste_disposal(user_id)
    elif choice == "Eco Points Menu":
        eco_points_menu(user_id)
    elif choice == "Waste Collection Schedule":
        show_waste_collection(user_id)
    elif choice == "Waste Tracking":
        show_waste_tracking(user_id)
    elif choice == "Logout":
        st.write("Logging out...")
        main_menu()

# Function to display the main menu
def main_menu():
    st.title("EcoTrack")
    st.write("Your daily recycling companion")
    choice = st.selectbox("Choose an option:", ["Create New User", "Login", "Exit"])
    
    if choice == "Create New User":
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        if st.button("Create Account"):
            if create_user(new_username, new_password):
                st.success("Account created successfully! You can now log in.")
            else:
                st.error("Error: Username already exists. Please try a different username.")
    elif choice == "Login":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user_id = login(username, password)
            if user_id:
                st.success(f"Login successful! Welcome, {username}.")
                user_dashboard(user_id)
            else:
                st.error("Invalid username or password. Please try again.")
    elif choice == "Exit":
        st.write("Goodbye!")
        st.stop()

if __name__ == "__main__":
    main_menu()