 EcoTrack: Smart Waste Management System

This is the backend for the EcoTrack project. It is built with Node.js, Express, and MongoDB and implements user authentication with JWT.

Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Server](#running-the-server)
- [API Endpoints](#api-endpoints)
- [Running Tests](#running-tests)
- [Folder Structure](#folder-structure)
- [Additional Notes](#additional-notes)

Features

- User Registration: `POST /auth/register`
- User Login: `POST /auth/login` (returns a JWT token)
- Protected Routes:  
  - Admin Dashboard: `GET /admin/dashboard` (accessible only by admin users)
  - User Profile: `GET /user/profile` (accessible by any logged-in user)
- **JWT-based authentication** with middleware

Prerequisites

- [Node.js](https://nodejs.org/) installed
- [MongoDB](https://www.mongodb.com/try/download/community) running locally (or a MongoDB Atlas URI)
- A code editor such as [VS Code](https://code.visualstudio.com/)

Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/ecotrack.git
   cd ecotrack
   ```

2. Install dependencies:

   ```bash
   npm install
   ```

Configuration

Create a `.env` file in the project root (if it doesn't already exist) and add the following:

```
MONGO_URI=mongodb://127.0.0.1:27017/ecotrack
JWT_SECRET=mysecretkey
PORT=5000
```

Make sure that MongoDB is running locally on port `27017` (or update `MONGO_URI` accordingly).

Running the Server

Manually

To start the server, run:

```bash
npm start
```

You should see output similar to:

```
🚀 Server running on port 5000
✅ MongoDB Connected
```

Using Nodemon (Auto Restart on Changes)

During development, you can use:

```bash
npm run dev
```

API Endpoints

- Test Route:
  - `GET /`
  - _Response:_ `"EcoTrack Server is Running 🚀"`

- User Registration:
  - `POST /auth/register`
  - _Body (JSON):_
    ```json
    {
      "username": "testuser",
      "password": "password123",
      "role": "user"
    }
    ```
  - _Response:_ `{ "message": "User registered" }`

- User Login:
  - `POST /auth/login`
  - _Body (JSON):_
    ```json
    {
      "username": "testuser",
      "password": "password123"
    }
    ```
  - _Response:_ `{ "token": "eyJhbGciOi...", "role": "user" }`

- Protected Admin Dashboard:
  - `GET /admin/dashboard`
  - _Headers:_  
    `Authorization: Bearer YOUR_JWT_TOKEN`
  - _Response:_ `{ "message": "Welcome Admin!" }`

- Protected User Profile:
  - `GET /user/profile`
  - _Headers:_  
    `Authorization: Bearer YOUR_JWT_TOKEN`
  - _Response:_ `{ "message": "Welcome user!", "user": { ... } }`

Running Tests

This project uses [Jest](https://jestjs.io/) and [Supertest](https://github.com/visionmedia/supertest) for unit testing.

To run the tests, execute:

```bash
npm test
```

This command will run all tests located in the `tests/` folder and display a coverage report.

Additional Notes

- Ensure MongoDB is running locally. If using MongoDB Compass, verify the connection URI.
- If you encounter issues, check that the file and folder names (e.g., `routes/auth.js` and `models/User.js`) match exactly.
- For testing, ensure that your `.env` file is correctly configured and loaded.

