const express = require('express');
const path = require('path');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// API Routes Placeholder
app.get('/api/status', (req, res) => {
    res.json({ 
        status: 'online', 
        version: '1.0.0',
        environment: 'migration-control-center',
        nodeVersion: process.version
    });
});

// Serve Angular App (for production build)
// In dev, we use concurrent proxy
app.use(express.static(path.join(__dirname, 'dist/migration-control-center/browser')));

app.get('*', (req, res) => {
    // Only serve index.html if not an API call
    if (!req.url.startsWith('/api')) {
        res.sendFile(path.join(__dirname, 'dist/migration-control-center/browser/index.html'));
    }
});

app.listen(PORT, () => {
    console.log(`🚀 Server running on http://localhost:${PORT}`);
    console.log(`🔧 Node Environment: ${process.version}`);
});
