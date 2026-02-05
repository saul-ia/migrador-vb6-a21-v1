const express = require('express');
const cors = require('cors');
const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

// Import Routes
const librosRoutes = require('./backend/routes/libros.routes');
const sociosRoutes = require('./backend/routes/socios.routes');
const authRoutes = require('./backend/routes/auth.routes'); // Added Auth Routes import
const prestamosRoutes = require('./backend/routes/prestamos.routes');

// Register Routes
app.use('/api/libros', librosRoutes);
app.use('/api/socios', sociosRoutes);
app.use('/api/auth', authRoutes); // Added Auth Routes registration
app.use('/api/prestamos', prestamosRoutes);

app.get('/', (req, res) => {
    res.send('Biblioteca API v1.0 is running');
});

app.listen(PORT, () => {
    console.log(`🚀 Server running on http://localhost:${PORT}`);
});
