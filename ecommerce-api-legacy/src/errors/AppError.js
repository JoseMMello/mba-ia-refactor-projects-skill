const DEFAULT_STATUS = 400;

class AppError extends Error {
    constructor(message, status = DEFAULT_STATUS, options = {}) {
        super(message, options);
        this.name = 'AppError';
        this.status = status;
    }
}

module.exports = AppError;
