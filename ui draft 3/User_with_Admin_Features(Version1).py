import sqlite3
import sys
from datetime import datetime
def connect_db():
    return sqlite3.connect("ecotrackDB.db")
    
def create_user():
    with connect_db() as conn:
        cursor = conn.cursor()
        
        username = input("Enter new username: ")
        password = input("Enter password: ")
        role = "user"
        
        try:
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
            user_id = cursor.lastrowid
            cursor.execute("INSERT INTO waste_tracking (user_id, recyclable_kg, non_recyclable_kg, current_total_kg) VALUES (?, 0, 0, 0)", (user_id,))
            cursor.execute("INSERT INTO eco_points (user_id, total_points) VALUES (?, 0)", (user_id,))
            conn.commit()
            print("User created successfully!")
        except sqlite3.IntegrityError:
            print("Error: Username already exists!")
    conn.close()

def login():
    conn = connect_db()
    cursor = conn.cursor()
    
    username = input("Enter username: ")
    password = input("Enter password: ")
    cursor.execute("SELECT id, username, password, role, company_name FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    
    if user and user[2] == password:
        print(f"Login successful! Welcome, {user[1]}.")
        conn.close()
        return user[0], user[3], user[4]  # Return user ID, role, company name
    else:
        print("Invalid username or password.")
        conn.close()
        return None, None, None

def show_waste_collection(user_id):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT time_of_day, day_of_week, day, month, waste_type FROM waste_collection_schedule ORDER BY date ASC LIMIT 5")
        schedules = cursor.fetchall()
        
        if schedules:
            print("\n===== Upcoming Waste Collection =====")
            for s in schedules:
                print(f" - {s[1]}, {s[2]} {s[3]} ({s[0]}): {s[4]}")
        else:
            print("No upcoming collection dates available.")

        search_confirm = input("Do you want to search for a specific waste collection date? (yes/no): ").lower()
        if search_confirm == "yes":
            search_waste_collection(user_id)
        elif search_confirm == "no":
            print("Returning to Menu...")
            user_options(user_id)
        else:
            print("Invalid choice. Please enter 'yes' or 'no'.")
              
def search_waste_collection(user_id):
    day = input("Enter the day to search (e.g., 5): ")
    month = input("Enter the month to search (e.g., February): ")
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT time_of_day, day_of_week, waste_type FROM waste_collection_schedule WHERE day = ? AND month = ?", (day, month))
        results = cursor.fetchall()
        
        if results:
            print("\nScheduled Waste Collection:")
            for r in results:
                print(f" - {r[1]} ({r[0]}): {r[2]}")
        else:
            print("No collection found for the given date.")
        user_options(user_id)
            
def show_waste_tracking(user_id):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT recyclable_kg, non_recyclable_kg, current_total_kg, total_recycled_kg FROM waste_tracking WHERE user_id = ?", (user_id,))
        tracking = cursor.fetchone()
        
        if tracking:
            print("\n===== Waste Tracking Information =====")
            print(f" - Recyclable Trash: {tracking[0]} kg")
            print(f" - Non-Recyclable Trash: {tracking[1]} kg")
            print(f" - Current Total Trash: {tracking[2]} kg")
            print(f" - Lifetime Recycled Trash: {tracking[3]} kg")
        else:
            print("No waste tracking data available.")

def show_eco_points(user_id):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT total_points FROM eco_points WHERE user_id = ?", (user_id,))
        points = cursor.fetchone()
        print(f"Your current EcoPoints: {points[0]}" if points else "No EcoPoints found.")

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
            print("\nYour Owned Vouchers:")
            for v in vouchers:
                status = "Used" if v[2] else "Not Used"
                print(f" - {v[0]} (Redeemed on: {v[1]}) [{status}]")
        else:
            print("You have no vouchers.")

def show_available_vouchers():
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, cost, stock FROM vouchers WHERE stock > 0")
        vouchers = cursor.fetchall()
        
        if vouchers:
            print("\nAvailable Vouchers:")
            for v in vouchers:
                print(f"{v[0]}. {v[1]} - {v[2]} points (Stock: {v[3]})")
        else:
            print("No vouchers available.")

def purchase_voucher(user_id):
    show_eco_points(user_id)
    show_available_vouchers()
    
    voucher_id = input("Enter the voucher ID to purchase: ")
    confirm = input("Are you sure you want to purchase this voucher? (yes/no): ").lower()
    if confirm != "yes":
        print("Purchase canceled.")
        return
    
    with connect_db() as conn:
        cursor = conn.cursor()
        
        # Get voucher cost and stock
        cursor.execute("SELECT cost, stock FROM vouchers WHERE id = ? AND stock > 0", (voucher_id,))
        voucher = cursor.fetchone()
        if not voucher:
            print("Invalid voucher ID or out of stock.")
            return
        
        cost, stock = voucher
        
        # Check user EcoPoints balance
        cursor.execute("SELECT total_points FROM eco_points WHERE user_id = ?", (user_id,))
        points = cursor.fetchone()[0]
        
        if points < cost:
            print("Insufficient EcoPoints.")
            return
        
        # Deduct EcoPoints, update stock, and insert redemption record
        cursor.execute("UPDATE eco_points SET total_points = total_points - ? WHERE user_id = ?", (cost, user_id))
        cursor.execute("UPDATE vouchers SET stock = stock - 1 WHERE id = ?", (voucher_id,))
        cursor.execute("INSERT INTO redeemed_vouchers (user_id, voucher_id, used) VALUES (?, ?, 0)", (user_id, voucher_id))
        conn.commit()
        
        print("Voucher redeemed successfully!")

def eco_points_menu(user_id):
    while True:
        print("\n===== Eco Points System =====")
        print("1. Show Total EcoPoints")
        print("2. Show Owned Vouchers")
        print("3. Show Available Vouchers")
        print("4. Purchase Voucher")
        print("5. Exit to Menu")
        choice = input("Enter choice: ")
        
        if choice == "1":
            show_eco_points(user_id)
        elif choice == "2":
            show_owned_vouchers(user_id)
        elif choice == "3":
            show_available_vouchers()
        elif choice == "4":
            purchase_voucher(user_id)
        elif choice == "5":
            print("Returning to menu...")
            break
        else:
            print("Invalid choice, try again.")

def user_dashboard(user_id):
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    cursor.execute("SELECT total_points FROM eco_points WHERE id = ?", (user_id,))
    ecopoints = cursor.fetchone()
    cursor.execute("SELECT recyclable_kg, non_recyclable_kg FROM waste_tracking WHERE user_id = ?", (user_id,))
    waste_data = cursor.fetchone()
    cursor.execute("SELECT time_of_day, day_of_week, waste_type FROM waste_collection_schedule ORDER BY date ASC LIMIT 1")
    schedule = cursor.fetchone()
    
    conn.close()
    
    if user and waste_data and schedule:
        print(f"\n===== Dashboard for {user[0]} =====")
        print(f" - EcoPoints: {ecopoints[0]}")
        print(f" - Recyclable Trash: {waste_data[0]} kg")
        print(f" - Non-Recyclable Trash: {waste_data[1]} kg")
        print(f" - Next Trash Collection Details: {schedule[1]}, {schedule[0]}. Please take out {schedule[2]} trash.")
    else:
        print("Error: Missing user or waste tracking data.")
    
    user_options(user_id)

def waste_disposal(user_id):
    while True:
        print("\nWaste Disposal:")
        print("1. Recyclable")
        print("2. Non-Recyclable")
        print("3. I Don't Know")
        print("4. Exit to Menu")
        choice = input("Enter choice: ")

        if choice == "4":
            print("Returning to menu...")
            break

        with connect_db() as conn:
            cursor = conn.cursor()

            recyclable = 1 if choice == "1" else 0 if choice == "2" else None
            weight_kg = float(input("Enter weight (kg): "))

            if recyclable is None:
                user_input = input("Enter the type of trash: ")
                cursor.execute("SELECT recyclable FROM recyclable_materials WHERE ? LIKE '%' || material || '%'", (user_input,))
                result = cursor.fetchone()
                if result is not None:
                    recyclable = result[0]
                else:
                    print("Data unavailable. Please check manually.")
                    continue  # Returns to the waste disposal menu

            column = "recyclable_kg" if recyclable else "non_recyclable_kg"
            cursor.execute(f"UPDATE waste_tracking SET {column} = {column} + ?, current_total_kg = current_total_kg + ? WHERE user_id = ?", (weight_kg, weight_kg, user_id))
            if recyclable:
                cursor.execute("UPDATE eco_points SET total_points = total_points + ? WHERE user_id = ?", (int(weight_kg), user_id))
                print(f"You earned {int(weight_kg)} EcoPoints!")
            conn.commit()
            print("Waste recorded successfully.")

        continue  # Ensures it loops back to the waste disposal menu
        
def user_options(user_id):
    while True:
        print("\n===== Menu =====")
        print("1. Dashboard")
        print("2. Waste Disposal")
        print("3. Eco Points Menu")
        print("4. Waste Collection Schedule")
        print("5. Waste Tracking")
        print("6. Logout")
        choice = input("Enter choice: ")
        
        if choice == "1":
            user_dashboard(user_id)
        elif choice == "2":
            waste_disposal(user_id)
        elif choice == "3":
            eco_points_menu(user_id)
        elif choice == "4":
            show_waste_collection(user_id)
        elif choice == "5":
            show_waste_tracking(user_id)
        elif choice == "6":
            print("Logging out...")
            main_menu()
        else:
            print("Invalid choice, try again.")

def company_dashboard(company_id, company_name):
    print(f"\n===== {company_name} Dashboard =====")
    
    today = datetime.today().strftime("%d")
    current_month = datetime.today().strftime("%B")

    with connect_db() as conn:
        cursor = conn.cursor()
        
        # Get the voucher with the least stock
        cursor.execute("SELECT name, cost, stock FROM vouchers WHERE company_id = ? ORDER BY stock ASC LIMIT 1", (company_id,))
        least_voucher = cursor.fetchone()
        
        print("\nLeast Stocked Voucher:")
        if least_voucher:
            print(f" - {least_voucher[0]} | Cost: {least_voucher[1]} points | Stock: {least_voucher[2]}")
        else:
            print("No vouchers available.")

        # Get collection schedule for today
        cursor.execute("SELECT time_of_day, waste_type FROM waste_collection_schedule WHERE company_id = ? AND day = ? AND month = ?", 
                       (company_id, today, current_month))
        today_schedule = cursor.fetchall()
        
        print("\nCollection Schedule for Today:")
        if today_schedule:
            for s in today_schedule:
                print(f" - {s[0]}: {s[1]}")
        else:
            print("No collection scheduled for today.")
    
    company_menu(company_id, company_name)

def company_menu(company_id, company_name):
    while True:
        print("\n===== Manage Company =====")
        print("1. Manage Collection Schedule")
        print("2. Manage Vouchers")
        print("3. Logout")
        
        choice = input("Enter choice: ")
        
        if choice == "1":
            manage_collection_schedule(company_id, company_name)
        elif choice == "2":
            manage_vouchers(company_id, company_name)
        elif choice == "3":
            print("Logging out...")
            break
        else:
            print("Invalid choice, try again.")

def manage_collection_schedule(company_id, company_name):
    while True:
        print("\n===== Manage Collection Schedule =====")
        print("1. View Collection Schedule")
        print("2. Add Collection Schedule")
        print("3. Remove Collection Schedule")
        print("4. Search Collection Schedule")
        print("5. Back to Menu")
        
        choice = input("Enter choice: ")
        
        if choice == "1":
            view_collection_schedule(company_id)
        elif choice == "2":
            add_collection_schedule(company_id)
        elif choice == "3":
            remove_collection_schedule(company_id)
        elif choice == "4":
            search_collection_schedule(company_id)
        elif choice == "5":
            break
        else:
            print("Invalid choice, try again.")

def view_collection_schedule(company_id):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT time_of_day, day_of_week, day, month, waste_type FROM waste_collection_schedule WHERE company_id = ?", (company_id,))
        schedules = cursor.fetchall()
        
        print("\nCollection Schedule:")
        if schedules:
            for s in schedules:
                print(f" - {s[1]}, {s[2]} {s[3]} ({s[0]}): {s[4]}")
        else:
            print("No scheduled collections.")

def add_collection_schedule(company_id):
    time_of_day = input("Enter Time of Day (Morning/Afternoon/Evening): ")
    day_of_week = input("Enter Day of the Week (e.g., Monday): ")
    day = input("Enter Day (e.g., 5): ")
    month = input("Enter Month (e.g., March): ")
    waste_type = input("Enter Waste Type (Recyclable/Non-Recyclable): ")

    # Dictionary to convert month name to number
    month_numbers = {
        "January": "01", "February": "02", "March": "03", "April": "04",
        "May": "05", "June": "06", "July": "07", "August": "08",
        "September": "09", "October": "10", "November": "11", "December": "12"
    }

    # Convert month to its numeric value
    month_num = month_numbers.get(month, None)
    
    if month_num is None:
        print("Invalid month entered. Please try again.")
        return

    day = day.zfill(2)

    full_date = f"2025-{month_num}-{day}"  # Format YYYY-MM-DD

    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO waste_collection_schedule (time_of_day, day_of_week, day, date, month, waste_type, company_id) VALUES (?, ?, ?, ?, ?, ?, ?)", 
               (time_of_day, day_of_week, day, full_date, month, waste_type, company_id))

        conn.commit()
        print("Collection schedule added successfully!")

def remove_collection_schedule(company_id):
    day = input("Enter Day to remove (e.g., 5): ")
    month = input("Enter Month to remove (e.g., March): ")

    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM waste_collection_schedule WHERE company_id = ? AND day = ? AND month = ?", (company_id, day, month))
        conn.commit()
        print("Collection schedule removed successfully!")

def search_collection_schedule(company_id):
    day = input("Enter Day to search (e.g., 5): ")
    month = input("Enter Month to search (e.g., March): ")

    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT time_of_day, day_of_week, waste_type FROM waste_collection_schedule WHERE company_id = ? AND day = ? AND month = ?", (company_id, day, month))
        results = cursor.fetchall()

        if results:
            print("\nScheduled Collection:")
            for r in results:
                print(f" - {r[1]} ({r[0]}): {r[2]}")
        else:
            print("No collection found for the given date.")

def manage_vouchers(company_id, company_name):
    while True:
        print("\n===== Manage Vouchers =====")
        print("1. View Current Vouchers")
        print("2. Add Voucher")
        print("3. Remove Voucher")
        print("4. Back to Menu")

        choice = input("Enter choice: ")

        if choice == "1":
            view_vouchers(company_id)
        elif choice == "2":
            add_voucher(company_id)
        elif choice == "3":
            remove_voucher(company_id)
        elif choice == "4":
            break
        else:
            print("Invalid choice, try again.")

def view_vouchers(company_id):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, cost, stock FROM vouchers WHERE company_id = ?", (company_id,))
        vouchers = cursor.fetchall()

        print("\nAvailable Vouchers:")
        if vouchers:
            for v in vouchers:
                print(f" - {v[0]} | Cost: {v[1]} points | Stock: {v[2]}")
        else:
            print("No vouchers available.")

def add_voucher(company_id):
    name = input("Enter Voucher Name: ")
    cost = int(input("Enter Voucher Cost: "))
    stock = int(input("Enter Stock Quantity: "))

    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO vouchers (name, cost, stock, company_id) VALUES (?, ?, ?, ?)", (name, cost, stock, company_id))
        conn.commit()
        print("Voucher added successfully!")

def remove_voucher(company_id):
    name = input("Enter Voucher Name to Remove: ")

    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM vouchers WHERE company_id = ? AND name = ?", (company_id, name))
        conn.commit()
        print("Voucher removed successfully!")

def main_menu():
    while True:
        print("===== Welcome to Ecotrack =====")
        print("1. Create New User")
        print("2. Login")
        print("3. Exit")
        choice = input("Enter choice: ")
        
        if choice == "1":
            create_user()
        elif choice == "2":
            user_id, role, company_name = login()
            if role == "company":
                company_dashboard(user_id, company_name)
            else:
                user_dashboard(user_id)
        elif choice == "3":
            print("Goodbye!")
            sys.exit()
        else:
            print("Invalid choice, try again.")

if __name__ == "__main__":
    main_menu()