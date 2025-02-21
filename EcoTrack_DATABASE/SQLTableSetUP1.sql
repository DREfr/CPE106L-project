-- 1. Users Table (Stores login credentials and EcoPoints balance)
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL, -- Store hashed password
    role TEXT CHECK(role IN ('user', 'admin')) NOT NULL,
    eco_points INTEGER DEFAULT 0
);

-- 2. Recyclable Materials Table (Predefined list of recyclable items)
CREATE TABLE recyclable_materials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    material TEXT UNIQUE NOT NULL,  -- E.g., "plastic", "cardboard", "paper"
    recyclable BOOLEAN NOT NULL DEFAULT 1  -- 1 = Recyclable, 0 = Non-recyclable
);

-- 3. User Waste Entries (Stores what users throw away)
CREATE TABLE user_waste_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    waste_type TEXT NOT NULL, -- User input (e.g., "plastic bottle")
    weight_kg REAL NOT NULL,
    recyclable BOOLEAN, -- Checked against recyclable_materials
    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 4. EcoPoints Table (Admin can modify user points)
CREATE TABLE eco_points (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    total_points INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 5. Vouchers Table (Available rewards for EcoPoints)
CREATE TABLE vouchers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,  
    cost INTEGER NOT NULL,  
    stock INTEGER NOT NULL  
);

-- 6. Redeemed Vouchers Table (Tracks user voucher redemptions)
CREATE TABLE redeemed_vouchers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    voucher_id INTEGER,
    date_redeemed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    used BOOLEAN DEFAULT 0, -- 0 = Not Used, 1 = Used
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (voucher_id) REFERENCES vouchers(id)
);

-- 7. Waste Collection Schedule Table (Pickup schedule based on time and waste type)
CREATE TABLE waste_collection_schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    time_of_day TEXT NOT NULL, -- "Morning", "Afternoon", "Evening"
    day_of_week TEXT NOT NULL, -- "Monday", "Tuesday", etc.
    day INTEGER NOT NULL, -- Numeric day (e.g., 2, 5, 19)
    date TEXT NOT NULL, -- Full date (YYYY-MM-DD format)
    month TEXT NOT NULL, -- "January", "February", etc.
    waste_type TEXT NOT NULL  -- "Plastic", "Glass", "Organic"
);

-- 8. Waste Tracking Table (Tracks user trash stats)
CREATE TABLE waste_tracking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    total_recycled_kg REAL DEFAULT 0,
    current_total_kg REAL DEFAULT 0,
    recyclable_kg REAL DEFAULT 0,
    non_recyclable_kg REAL DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
