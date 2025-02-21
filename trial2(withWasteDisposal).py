import sqlite3

def connect_db():
    return sqlite3.connect("ecotrackDB.db")

def create_user():
    conn = connect_db()
    cursor = conn.cursor()
    
    username = input("Enter new username: ")
    password = input("Enter password: ")
    role = input("Enter role (user/admin): ")
    
    try:
        cursor.execute("INSERT INTO users (username, password, role, eco_points) VALUES (?, ?, ?, 0)", (username, password, role))
        cursor.execute("INSERT INTO waste_tracking (user_id, recyclable_kg, non_recyclable_kg, current_total_kg) VALUES (?, 0, 0, 0)", (cursor.lastrowid,))
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

def user_dashboard(user_id):
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT username, eco_points FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    cursor.execute("SELECT recyclable_kg, non_recyclable_kg FROM waste_tracking WHERE user_id = ?", (user_id,))
    waste_data = cursor.fetchone()
    cursor.execute("SELECT time_of_day, day_of_week, waste_type FROM waste_collection_schedule ORDER BY date ASC LIMIT 1")
    schedule = cursor.fetchone()
    
    conn.close()
    
    if user and waste_data and schedule:
        print(f"\n===== Dashboard for {user[0]} =====")
        print(f" - EcoPoints: {user[1]}")
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
            conn.commit()

            print("Waste recorded successfully.")

        continue  # Ensures it loops back to the waste disposal menu
        

def user_options(user_id):
    while True:
        print("\n1. Waste Disposal")
        print("2. Logout")
        choice = input("Enter choice: ")
        
        if choice == "1":
            waste_disposal(user_id)
        elif choice == "2":
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
            break
        else:
            print("Invalid choice, try again.")

if __name__ == "__main__":
    main_menu()