// =============================================================================
// EXPRESS SERVER - Biblioteca Backend
// Migrated from VB6 + Access to Express 5 + SQLite/Prisma
// =============================================================================

import express, { type Express, type Request, type Response, type NextFunction } from 'express';
import cors from 'cors';
import { pino } from 'pino';
import { PrismaClient } from '@prisma/client';
import swaggerUi from 'swagger-ui-express';
import YAML from 'yamljs';
import path from 'path';

// Import routes
import claveRoutes from './routes/clave.routes.js';
import clienteRoutes from './routes/cliente.routes.js';
import libroRoutes from './routes/libro.routes.js';

// =============================================================================
// CONFIGURATION
// =============================================================================

const PORT = process.env.PORT || 3000;
const NODE_ENV = process.env.NODE_ENV || 'development';

// Logger
const logger = pino({
    transport: NODE_ENV === 'development' ? { target: 'pino-pretty' } : undefined,
});

// Prisma Client (singleton)
export const prisma = new PrismaClient({
    log: NODE_ENV === 'development' ? ['query', 'info', 'warn', 'error'] : ['error'],
});

// Express App
const app: Express = express();

// =============================================================================
// MIDDLEWARE
// =============================================================================

app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Request logging
app.use((req: Request, _res: Response, next: NextFunction) => {
    logger.info({ method: req.method, url: req.url }, 'Incoming request');
    next();
});

// =============================================================================
// SWAGGER DOCUMENTATION
// =============================================================================

try {
    const swaggerDocument = YAML.load(path.join(__dirname, 'swagger.yaml'));
    app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerDocument));
    logger.info('📚 Swagger docs available at /api-docs');
} catch (e) {
    logger.warn('⚠️ Swagger YAML not found, skipping API docs');
}

// =============================================================================
// ROUTES
// =============================================================================

// Health check
app.get('/health', (_req: Request, res: Response) => {
    res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// API Routes
app.use('/api/claves', claveRoutes);
app.use('/api/clientes', clienteRoutes);
app.use('/api/libros', libroRoutes);

// =============================================================================
// ERROR HANDLING
// =============================================================================

// 404 Handler
app.use((_req: Request, res: Response) => {
    res.status(404).json({ error: 'Not Found' });
});

// Global Error Handler
app.use((err: Error, _req: Request, res: Response, _next: NextFunction) => {
    logger.error({ error: err.message, stack: err.stack }, 'Unhandled error');
    res.status(500).json({ error: 'Internal Server Error' });
});

// =============================================================================
// SERVER STARTUP
// =============================================================================

async function main() {
    try {
        // Test database connection
        await prisma.$connect();
        logger.info('✅ Database connected');

        app.listen(PORT, () => {
            logger.info(`🚀 Server running on http://localhost:${PORT}`);
            logger.info(`📚 API Docs: http://localhost:${PORT}/api-docs`);
        });
    } catch (error) {
        logger.error({ error }, '❌ Failed to start server');
        process.exit(1);
    }
}

// Graceful shutdown
process.on('SIGTERM', async () => {
    logger.info('SIGTERM received, shutting down...');
    await prisma.$disconnect();
    process.exit(0);
});

main();
