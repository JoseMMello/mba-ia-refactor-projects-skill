const crypto = require('crypto');
const config = require('../config');
const { PAYMENT_STATUS } = require('../models/paymentStatus');

const RANDOM_PASSWORD_BYTES = 24;

const SEED_USER = { name: 'Leonan', email: 'leonan@fullcycle.com.br' };
const SEED_COURSES = [
    { title: 'Clean Architecture', price: 997.00, active: 1 },
    { title: 'Docker', price: 497.00, active: 1 }
];

// Loads the initial data only when the database is empty.
async function seedDatabase({ db, userModel, courseModel, enrollmentModel, paymentModel }) {
    const [users, courses] = await Promise.all([userModel.count(), courseModel.count()]);
    if (users > 0 || courses > 0) return;

    const password = config.seedUserPassword || crypto.randomBytes(RANDOM_PASSWORD_BYTES).toString('hex');

    await db.transaction(async (tx) => {
        const userId = await userModel.create({ ...SEED_USER, password }, tx);

        const courseIds = [];
        for (const course of SEED_COURSES) {
            courseIds.push(await courseModel.create(course, tx));
        }

        const firstCourseId = courseIds[0];
        const enrollmentId = await enrollmentModel.create({ userId, courseId: firstCourseId }, tx);
        await paymentModel.create({
            enrollmentId,
            amount: SEED_COURSES[0].price,
            status: PAYMENT_STATUS.PAID
        }, tx);
    });
}

module.exports = { seedDatabase };
