const DEFAULT_PORT = 3000;
const DEFAULT_DATABASE_PATH = ':memory:';
const DEFAULT_LOG_LEVEL = 'info';

function loadEnvFile() {
    if (typeof process.loadEnvFile !== 'function') return;
    try {
        process.loadEnvFile();
    } catch (err) {
        if (err.code !== 'ENOENT') throw err;
    }
}

loadEnvFile();

const config = {
    port: Number(process.env.PORT) || DEFAULT_PORT,
    databasePath: process.env.DATABASE_PATH || DEFAULT_DATABASE_PATH,
    logLevel: process.env.LOG_LEVEL || DEFAULT_LOG_LEVEL,
    adminToken: process.env.ADMIN_TOKEN || '',
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',
    seedUserPassword: process.env.SEED_USER_PASSWORD || ''
};

module.exports = config;
