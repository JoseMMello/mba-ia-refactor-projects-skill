const crypto = require('crypto');
const config = require('../config');
const AppError = require('../errors/AppError');

const ADMIN_TOKEN_HEADER = 'x-admin-token';
const HTTP_FORBIDDEN = 403;

function digest(value) {
    return crypto.createHash('sha256').update(value).digest();
}

// Allows the request only when it carries the admin token from the configuration.
// With no token configured, every request is refused.
function requireAdmin(req, res, next) {
    const received = req.get(ADMIN_TOKEN_HEADER) || '';
    const authorized = Boolean(config.adminToken)
        && crypto.timingSafeEqual(digest(received), digest(config.adminToken));

    if (!authorized) return next(new AppError('Forbidden', HTTP_FORBIDDEN));
    next();
}

module.exports = requireAdmin;
