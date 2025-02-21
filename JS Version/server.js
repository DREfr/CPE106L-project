require('dotenv').config(); // Load environment variables

const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const { verifyToken, isAdmin } = require('./middleware/authMiddleware'); // Import middleware

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors()); // ✅ Move CORS middleware here
app.use(express.json()); // Enable JSON request parsing

// ✅ Connect to MongoDB with better options
mongoose.connect(process.env.MONGO_URI, {
    useNewUrlParser: true,
    useUnifiedTopology: true,
})
    .then(() => console.log('✅ MongoDB Connected'))
    .catch(err => console.log('❌ MongoDB Connection Error:', err));

// ✅ Test Route (To Check If Server is Running)
app.get('/', (req, res) => {
    res.send("EcoTrack Server is Running 🚀");
});

// ✅ Import & Use Authentication Routes
const authRoutes = require('./routes/auth');
app.use('/auth', authRoutes);

// ✅ Protected Admin Route (Only for Admins)
app.get('/admin/dashboard', verifyToken, isAdmin, (req, res) => {
    res.json({ message: "Welcome Admin!" });
});

// ✅ Protected User Profile Route (For Any Logged-in User)
app.get('/user/profile', verifyToken, (req, res) => {
    res.json({ message: `Welcome ${req.user.role}!`, user: req.user });
});

// ✅ Start the Server
app.listen(PORT, () => console.log(`🚀 Server running on port ${PORT}`));
