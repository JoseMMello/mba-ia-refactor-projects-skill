const AppError = require('../../errors/AppError');

const POSITIVE_INTEGER_PATTERN = /^[1-9]\d*$/;

function validateId(value) {
    if (typeof value !== 'string' || !POSITIVE_INTEGER_PATTERN.test(value)) {
        throw new AppError('Bad Request');
    }
    return Number(value);
}

module.exports = { validateId };
