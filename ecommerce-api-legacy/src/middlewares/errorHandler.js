const { STATUS_CODES } = require('http');
const AppError = require('../errors/AppError');
const logger = require('../logger');

const HTTP_INTERNAL_ERROR = 500;
const DATABASE_ERROR_MESSAGE = 'Erro DB';
const INTERNAL_ERROR_MESSAGE = 'Erro interno';

function isClientError(status) {
    return Number.isInteger(status) && status >= 400 && status < 500;
}

function isDatabaseError(err) {
    return typeof err.code === 'string' && err.code.startsWith('SQLITE');
}

// Single place that turns errors into responses. Error bodies are plain text, as in the
// original API, and never carry internal details.
function errorHandler(err, req, res, next) {
    if (res.headersSent) return next(err);

    if (err instanceof AppError) {
        if (err.status >= HTTP_INTERNAL_ERROR) logger.error(err.message, err.cause || err);
        return res.status(err.status).send(err.message);
    }

    // Errors raised by Express itself, such as a malformed JSON body.
    if (isClientError(err.status)) {
        return res.status(err.status).send(STATUS_CODES[err.status] || 'Bad Request');
    }

    logger.error(`Unhandled error on ${req.method} ${req.path}`, err);
    res.status(HTTP_INTERNAL_ERROR)
        .send(isDatabaseError(err) ? DATABASE_ERROR_MESSAGE : INTERNAL_ERROR_MESSAGE);
}

module.exports = errorHandler;
