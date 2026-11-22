const AppError = require('../../errors/AppError');

const EMAIL_PATTERN = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
const POSITIVE_INTEGER_PATTERN = /^[1-9]\d*$/;

function isFilledString(value) {
    return typeof value === 'string' && value.trim() !== '';
}

function badRequest() {
    return new AppError('Bad Request');
}

// Validates the checkout body and returns it with meaningful names.
// `pwd` is optional here: the service requires it only when the user does not exist yet.
function validateCheckout(body) {
    if (!body || typeof body !== 'object' || Array.isArray(body)) throw badRequest();

    const { usr, eml, pwd, c_id: rawCourseId, card } = body;

    if (!isFilledString(usr) || !isFilledString(eml) || !isFilledString(card)) throw badRequest();
    if (!EMAIL_PATTERN.test(eml)) throw badRequest();
    if (pwd !== undefined && pwd !== null && pwd !== '' && typeof pwd !== 'string') throw badRequest();
    if (!POSITIVE_INTEGER_PATTERN.test(String(rawCourseId))) throw badRequest();
    if (typeof rawCourseId !== 'number' && typeof rawCourseId !== 'string') throw badRequest();

    return {
        name: usr,
        email: eml,
        password: pwd || null,
        courseId: Number(rawCourseId),
        card
    };
}

module.exports = { validateCheckout };
