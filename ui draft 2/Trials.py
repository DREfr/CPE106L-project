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