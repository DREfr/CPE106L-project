# EcoTrack: Smart Waste Management System

## Overview

EcoTrack is a **Streamlit-based** web application designed to promote efficient waste management. The system allows **users** to track waste disposal, earn EcoPoints, and redeem vouchers, while **companies** can manage waste collection schedules and vouchers. The system is backed by an **SQLite database** to store user and company data.

## Web App Link
[EcoTrack Web App](https://cpe106l-project-2j9tfprrs8ossxxma9swsn.streamlit.app/)


## Features

### User Features

- **User Registration & Login**
- **User Dashboard** (Track EcoPoints & waste statistics)
- **Waste Disposal System** (Classify & record waste)
- **EcoPoints System** (Earn & redeem points)
- **Waste Collection Schedule** (View & search schedules)
- **Waste Tracking** (Monitor total and lifetime waste)

### Company Features

- **Company Dashboard** (Manage waste collection & vouchers)
- **Manage Collection Schedule** (View, add, remove, and search collection schedules)
- **Manage Vouchers** (View, add, and remove vouchers)

## Installation & Setup

### 1. Clone the Repository

```sh
git clone https://github.com/yourusername/EcoTrack.git
cd EcoTrack
```

### 2. Create a Virtual Environment (Recommended)

```sh
python -m venv venv
```

### 3. Activate Virtual Environment

- **Windows (CMD):**
  ```sh
  venv\Scripts\activate
  ```
- **Mac/Linux:**
  ```sh
  source venv/bin/activate
  ```

### 4. Install Dependencies Manually

```sh
pip install streamlit sqlite3 datetime
```

### 5. Run the Application

```sh
streamlit run EcoTrackApp.py
```

## Dependencies

Make sure you have the following installed:

- **Python 3.x**
- **Streamlit** (for UI)
- **SQLite3** (for database handling)
- **Datetime** (for handling timestamps)

## Database Setup

The project uses an **SQLite database (`ecotrackDB.db`)** which is already included. If needed, you can manually inspect or modify the database using:

```sh
sqlite3 ecotrackDB.db
```

## How to Use

### User Flow

1. **Register/Login** to access features.
2. **Track & Dispose of Waste**
3. **Earn EcoPoints** and **redeem vouchers**
4. **Monitor waste collection schedules**

### Company Flow

1. **Login as a company account**
2. **Manage waste collection schedules**
3. **Add/remove vouchers** for users

## Troubleshooting

- If **Streamlit does not run**, ensure the virtual environment is activated.
- If **database errors occur**, ensure `ecotrackDB.db` is in the project directory.
- If missing dependencies, reinstall with:
  ```sh
  pip install streamlit sqlite3 datetime
  ```

## License

This project is open-source under the **MIT License**.

## Authors

Sean Dela Cruz
Gino Andre Valencerina Jimenez
Juan Miguel Ocampo
John Louie Fernando Reyes

