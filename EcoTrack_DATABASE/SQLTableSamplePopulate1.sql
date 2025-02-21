-- Insert Users (4 Users: 2 Regular, 2 Admins)
INSERT INTO users (username, password, role, eco_points) 
VALUES 
    ('john_doe', 'hashed_password_123', 'user', 10),
    ('alice_green', 'hashed_password_456', 'user', 20),
    ('admin_eco1', 'hashed_admin_pass1', 'admin', 0),
    ('admin_eco2', 'hashed_admin_pass2', 'admin', 0);

-- Insert Recyclable Materials (4 Common Materials)
INSERT INTO recyclable_materials (material, recyclable) 
VALUES 
    ('plastic', 1),
    ('cardboard', 1),
    ('glass', 1),
    ('food waste', 0); -- Not recyclable

-- Insert User Waste Entries (4 Waste Submissions)
INSERT INTO user_waste_entries (user_id, waste_type, weight_kg, recyclable) 
VALUES 
    (1, 'plastic bottle', 2.5, 1),
    (2, 'cardboard box', 1.2, 1),
    (1, 'glass jar', 0.8, 1),
    (2, 'food waste', 3.0, 0);

-- Insert EcoPoints Data (4 Users' Points)
INSERT INTO eco_points (user_id, total_points) 
VALUES 
    (1, 15),
    (2, 25),
    (3, 0),  -- Admin, no points
    (4, 0);  -- Admin, no points

-- Insert Vouchers (4 Rewards Available)
INSERT INTO vouchers (name, cost, stock) 
VALUES 
    ('Eco-friendly Tote Bag', 50, 20),
    ('Discount Coupon', 30, 50),
    ('Reusable Straw Set', 40, 15),
    ('Water Bottle', 60, 10);

-- Insert Redeemed Vouchers (Users Redeeming 4 Vouchers)
INSERT INTO redeemed_vouchers (user_id, voucher_id, date_redeemed, used) 
VALUES 
    (1, 1, '2025-02-15 10:30:00', 1),  -- Used
    (2, 2, '2025-02-16 11:00:00', 0),  -- Not used
    (1, 3, '2025-02-17 08:45:00', 1),  -- Used
    (2, 4, '2025-02-18 09:30:00', 0);  -- Not used

-- Insert Waste Collection Schedule (4 Scheduled Pickups)
INSERT INTO waste_collection_schedule (time_of_day, day_of_week, day, date, month, waste_type)
VALUES 
    ('Morning', 'Monday', 5, '2025-02-05', 'February', 'Recyclable'),
    ('Afternoon', 'Wednesday', 7, '2025-02-07', 'February', 'Recyclable'),
    ('Evening', 'Friday', 9, '2025-02-09', 'February', 'Non-Recyclable'),
    ('Morning', 'Tuesday', 12, '2025-02-12', 'February', 'Recyclable');

-- Insert Waste Tracking Data (4 Users' Trash Stats)
INSERT INTO waste_tracking (user_id, total_recycled_kg, current_total_kg, recyclable_kg, non_recyclable_kg)
VALUES 
    (1, 10.5, 2.5, 2.5, 0),
    (2, 8.2, 3.2, 1.2, 2.0),
    (3, 0, 0, 0, 0),  -- Admin, no waste tracking
    (4, 0, 0, 0, 0);  -- Admin, no waste tracking
