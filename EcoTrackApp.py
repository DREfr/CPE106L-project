import streamlit as st
import sqlite3
import gdown
import os

DB_PATH = "ecotrackDB.db"
GOOGLE_DRIVE_FILE_ID = "1PNq13Bb96DJnCieol3bwEgq-kG78FsgL"

def download_db():
    if not os.path.exists(DB_PATH):  
        url = f"https://drive.google.com/uc?id={GOOGLE_DRIVE_FILE_ID}"
        gdown.download(url, DB_PATH, quiet=False)
        print("Database downloaded from Google Drive.")

def connect_db():
    download_db()  
    return sqlite3.connect(DB_PATH, check_same_thread=False)


#------------------LOGIN-------------------
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

#------------USER SIDE FEATURES------------

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

def waste_disposal(user_id):
    st.subheader("Waste Disposal")

    disposal_choice = st.radio("Select Waste Type:", ["Recyclable", "Non-Recyclable", "I Don't Know"])
    weight_kg = st.number_input("Enter weight (kg):", min_value=0.1, format="%.2f")

    if disposal_choice == "I Don't Know":
        user_input = st.text_input("Enter the type of trash:")
        if st.button("Check"):
            with connect_db() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT recyclable FROM recyclable_materials WHERE ? LIKE '%' || material || '%'", (user_input,))
                result = cursor.fetchone()

                if result is not None:
                    recyclable = result[0]
                    st.success(f"The item is {'Recyclable' if recyclable else 'Non-Recyclable'}.")
                else:
                    st.warning("Data unavailable. Please check manually.")
                    return  # Stops further processing

    elif st.button("Submit Waste"):
        with connect_db() as conn:
            cursor = conn.cursor()
            recyclable = 1 if disposal_choice == "Recyclable" else 0
            column = "recyclable_kg" if recyclable else "non_recyclable_kg"

            # Update waste tracking
            cursor.execute(f"UPDATE waste_tracking SET {column} = {column} + ?, current_total_kg = current_total_kg + ? WHERE user_id = ?", (weight_kg, weight_kg, user_id))

            # If recyclable, add EcoPoints
            if recyclable:
                cursor.execute("UPDATE eco_points SET total_points = total_points + ? WHERE user_id = ?", (int(weight_kg), user_id))
                st.success(f"You earned {int(weight_kg)} EcoPoints!")

            conn.commit()
            st.success("Waste recorded successfully.")

def eco_points_page(user_id):
    st.subheader("Eco Points System")

    # Fetch current EcoPoints
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT total_points FROM eco_points WHERE user_id = ?", (user_id,))
        points = cursor.fetchone()
        points = points[0] if points else 0
    st.write(f"**Your current EcoPoints:** {points}")

    # Show owned vouchers
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
        st.write("### Your Owned Vouchers")
        for v in vouchers:
            status = "✅ Used" if v[2] else "❌ Not Used"
            st.write(f"- **{v[0]}** (Redeemed on: {v[1]}) {status}")
    else:
        st.write("You have no vouchers.")

    # Show available vouchers
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, cost, stock FROM vouchers WHERE stock > 0")
        vouchers = cursor.fetchall()

    if vouchers:
        st.write("### Available Vouchers")
        for v in vouchers:
            st.write(f"**{v[1]}** - {v[2]} EcoPoints (Stock: {v[3]})")

        # Redeem a voucher
        voucher_options = {f"{v[1]} ({v[2]} pts)": v[0] for v in vouchers}
        selected_voucher = st.selectbox("Select a voucher to redeem:", list(voucher_options.keys()))
        
        if st.button("Redeem Voucher"):
            voucher_id = voucher_options[selected_voucher]
            with connect_db() as conn:
                cursor = conn.cursor()

                # Get voucher cost & stock
                cursor.execute("SELECT cost, stock FROM vouchers WHERE id = ?", (voucher_id,))
                voucher = cursor.fetchone()
                if not voucher:
                    st.error("Invalid voucher selection or out of stock.")
                    return
                
                cost, stock = voucher

                # Check if user has enough points
                if points < cost:
                    st.error("Insufficient EcoPoints.")
                    return
                
                # Process redemption
                cursor.execute("UPDATE eco_points SET total_points = total_points - ? WHERE user_id = ?", (cost, user_id))
                cursor.execute("UPDATE vouchers SET stock = stock - 1 WHERE id = ?", (voucher_id,))
                cursor.execute("INSERT INTO redeemed_vouchers (user_id, voucher_id, used) VALUES (?, ?, 0)", (user_id, voucher_id))
                conn.commit()

            st.success("Voucher redeemed successfully! 🎉")
            st.rerun()  # Refresh page to update points & vouchers

def waste_schedule_page(user_id):
    st.subheader("Waste Collection Schedule")

    # Fetch the next 5 collection schedules
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT time_of_day, day_of_week, day, month, waste_type FROM waste_collection_schedule ORDER BY date ASC LIMIT 5")
        schedules = cursor.fetchall()

    if schedules:
        st.write("### Upcoming Waste Collection")
        for s in schedules:
            st.write(f"- **{s[1]}, {s[2]} {s[3]} ({s[0]})**: {s[4]}")
    else:
        st.warning("No upcoming collection dates available.")

    # Search for specific waste collection
    st.write("### Search for a Waste Collection Date")
    day = st.text_input("Enter day (e.g., 5)")
    month = st.text_input("Enter month (e.g., February)")

    if st.button("Search Collection Date"):
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT time_of_day, day_of_week, waste_type FROM waste_collection_schedule WHERE day = ? AND month = ?", (day, month))
            results = cursor.fetchall()

        if results:
            st.write("### Scheduled Waste Collection")
            for r in results:
                st.write(f"- **{r[1]} ({r[0]})**: {r[2]}")
        else:
            st.warning("No collection found for the given date.")

def waste_tracking_page(user_id):
    st.subheader("Waste Tracking Information")

    # Fetch waste tracking data
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT recyclable_kg, non_recyclable_kg, current_total_kg, total_recycled_kg FROM waste_tracking WHERE user_id = ?", (user_id,))
        tracking = cursor.fetchone()

    if tracking:
        st.write(f"♻ **Recyclable Trash:** {tracking[0]} kg")
        st.write(f"🚮 **Non-Recyclable Trash:** {tracking[1]} kg")
        st.write(f"📊 **Current Total Trash:** {tracking[2]} kg")
        st.write(f"🏆 **Lifetime Recycled Trash:** {tracking[3]} kg")
    else:
        st.warning("No waste tracking data available.")

#---------COMPANY SIDE FEATURES-----------

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

   
def manage_collection_schedule(company_id, company_name):
    st.subheader(f"Manage Collection Schedule - {company_name}")

    menu_options = ["View Collection Schedule", "Add Collection Schedule", "Remove Collection Schedule", "Search Collection Schedule"]
    choice = st.selectbox("Select an option:", menu_options)

    if choice == "View Collection Schedule":
        view_collection_schedule(company_id)

    elif choice == "Add Collection Schedule":
        add_collection_schedule(company_id)

    elif choice == "Remove Collection Schedule":
        remove_collection_schedule(company_id)

    elif choice == "Search Collection Schedule":
        search_collection_schedule(company_id)

def view_collection_schedule(company_id):
    st.write("### Current Collection Schedule")

    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT time_of_day, day_of_week, day, month, waste_type FROM waste_collection_schedule WHERE company_id = ?", (company_id,))
        schedules = cursor.fetchall()

    if schedules:
        for s in schedules:
            st.write(f"- **{s[1]}, {s[2]} {s[3]} ({s[0]})**: {s[4]}")
    else:
        st.warning("No scheduled collections.")

def add_collection_schedule(company_id):
    st.write("### Add New Collection Schedule")

    time_of_day = st.selectbox("Select Time of Day:", ["Morning", "Afternoon", "Evening"])
    day_of_week = st.text_input("Enter Day of the Week (e.g., Monday):")
    day = st.text_input("Enter Day (e.g., 5):")
    month = st.text_input("Enter Month (e.g., March):")
    waste_type = st.selectbox("Select Waste Type:", ["Recyclable", "Non-Recyclable"])

    month_numbers = {
        "January": "01", "February": "02", "March": "03", "April": "04",
        "May": "05", "June": "06", "July": "07", "August": "08",
        "September": "09", "October": "10", "November": "11", "December": "12"
    }

    month_num = month_numbers.get(month)
    if not month_num:
        st.error("Invalid month entered.")
        return

    day = day.zfill(2)
    full_date = f"2025-{month_num}-{day}"

    if st.button("Add Schedule"):
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO waste_collection_schedule (time_of_day, day_of_week, day, date, month, waste_type, company_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (time_of_day, day_of_week, day, full_date, month, waste_type, company_id),
            )
            conn.commit()
        st.success("Collection schedule added successfully!")

def remove_collection_schedule(company_id):
    st.write("### Remove Collection Schedule")

    day = st.text_input("Enter Day to Remove (e.g., 5):")
    month = st.text_input("Enter Month to Remove (e.g., March):")

    if st.button("Remove Schedule"):
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM waste_collection_schedule WHERE company_id = ? AND day = ? AND month = ?", (company_id, day, month))
            conn.commit()
        st.success("Collection schedule removed successfully!")

def search_collection_schedule(company_id):
    st.write("### Search Collection Schedule")

    day = st.text_input("Enter Day to Search (e.g., 5):")
    month = st.text_input("Enter Month to Search (e.g., March):")

    if st.button("Search"):
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT time_of_day, day_of_week, waste_type FROM waste_collection_schedule WHERE company_id = ? AND day = ? AND month = ?",
                (company_id, day, month),
            )
            results = cursor.fetchall()

        if results:
            st.write("### Scheduled Collection:")
            for r in results:
                st.write(f"- **{r[1]} ({r[0]})**: {r[2]}")
        else:
            st.warning("No collection found for the given date.")

def view_vouchers(company_id):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, cost, stock FROM vouchers WHERE company_id = ?", (company_id,))
        vouchers = cursor.fetchall()
        
    st.subheader("Available Vouchers")
    if vouchers:
        for v in vouchers:
            st.write(f"**{v[0]}** | Cost: {v[1]} points | Stock: {v[2]}")
    else:
        st.write("No vouchers available.")

def add_voucher(company_id):
    st.subheader("Add Voucher")
    name = st.text_input("Voucher Name")
    cost = st.number_input("Voucher Cost", min_value=1, step=1)
    stock = st.number_input("Stock Quantity", min_value=1, step=1)
    
    if st.button("Add Voucher"):
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO vouchers (name, cost, stock, company_id) VALUES (?, ?, ?, ?)", (name, cost, stock, company_id))
            conn.commit()
        st.success("Voucher added successfully!")

def remove_voucher(company_id):
    st.subheader("Remove Voucher")
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM vouchers WHERE company_id = ?", (company_id,))
        vouchers = cursor.fetchall()
    
    voucher_names = [v[0] for v in vouchers]
    if voucher_names:
        selected_voucher = st.selectbox("Select Voucher to Remove", voucher_names)
        if st.button("Remove Voucher"):
            with connect_db() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM vouchers WHERE company_id = ? AND name = ?", (company_id, selected_voucher))
                conn.commit()
            st.success("Voucher removed successfully!")
    else:
        st.write("No vouchers available to remove.")

def manage_vouchers(company_id, company_name):
    st.subheader(f"Manage Vouchers - {company_name}")
    view_vouchers(company_id)
    st.divider()
    add_voucher(company_id)
    st.divider()
    remove_voucher(company_id)


#------------------MAIN-------------------

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
   
    #------SIDE BAR CHOICES (POST LOGIN)------

    elif choice == "Dashboard":
        if st.session_state.role == "company":
            company_dashboard(st.session_state.user_id, st.session_state.company_name)
        else:
            user_dashboard(st.session_state.user_id)

    
    elif choice == "Waste Disposal":
        waste_disposal(st.session_state.user_id)
    elif choice == "Eco Points":
        eco_points_page(st.session_state.user_id)
    elif choice == "Waste Schedule":
        waste_schedule_page(st.session_state.user_id)
    elif choice == "Waste Tracking":
        waste_tracking_page(st.session_state.user_id)


    elif choice == "Manage Collection Schedule":
        manage_collection_schedule(st.session_state.user_id, st.session_state.company_name)
    elif choice == "Manage Vouchers":
        manage_vouchers(st.session_state.user_id, st.session_state.company_name)


    elif choice == "Logout":
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

if __name__ == "__main__":
    main()
