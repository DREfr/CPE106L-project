import sqlite3
import sys

def connect_db():
    return sqlite3.connect("ecotrackDB.db")

def create_user():
    with connect_db() as conn:
        cursor = conn.cursor()
        
        username = input("Enter new username: ")
        password = input("Enter password: ")
        role = input("Enter role (user/admin): ")
        
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
    cursor.execute("SELECT id, username, password FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    
    if user and user[2] == password:
        print(f"Login successful! Welcome, {user[1]}.")
        conn.close()
        return user[0]  # Return user ID
    else:
        print("Invalid username or password.")
        conn.close()
        return None

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
        print("\nEco Points System:")
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
        print("4. Logout")
        choice = input("Enter choice: ")
        
        if choice == "1":
            user_dashboard(user_id)
        elif choice == "2":
            waste_disposal(user_id)
        elif choice == "3":
            eco_points_menu(user_id)
        elif choice == "4":
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
            user_id = login()
            if user_id:
                user_dashboard(user_id)
        elif choice == "3":
            print("Goodbye!")
            sys.exit()
        else:
            print("Invalid choice, try again.")

if __name__ == "__main__":
    main_menu()