const config = require('./config');

const LEVELS = { debug: 10, info: 20, warn: 30, error: 40 };
const threshold = LEVELS[config.logLevel] || LEVELS.info;

function write(level, stream, message, error) {
    if (LEVELS[level] < threshold) return;
    const detail = error ? ` ${error.stack || error.message || error}` : '';
    stream.write(`${new Date().toISOString()} [${level.toUpperCase()}] ${message}${detail}\n`);
}

module.exports = {
    debug: (message) => write('debug', process.stdout, message),
    info: (message) => write('info', process.stdout, message),
    warn: (message, error) => write('warn', process.stderr, message, error),
    error: (message, error) => write('error', process.stderr, message, error)
};
