const AppError = require('../errors/AppError');
const { PAYMENT_STATUS } = require('../models/paymentStatus');

const HTTP_BAD_REQUEST = 400;
const HTTP_NOT_FOUND = 404;
const HTTP_INTERNAL_ERROR = 500;

function failWith(message) {
    return (cause) => {
        throw new AppError(message, HTTP_INTERNAL_ERROR, { cause });
    };
}

function createCheckoutService({
    db, courseModel, userModel, enrollmentModel, paymentModel, auditLogModel, paymentService, logger
}) {
    return {
        async checkout({ name, email, password, courseId, card }) {
            const course = await courseModel.findActiveById(courseId).catch(failWith('Erro DB'));
            if (!course) throw new AppError('Curso não encontrado', HTTP_NOT_FOUND);

            const existingUser = await userModel.findByEmail(email).catch(failWith('Erro DB'));
            if (!existingUser && !password) throw new AppError('Bad Request', HTTP_BAD_REQUEST);

            const status = paymentService.authorize(card);
            if (status === PAYMENT_STATUS.DENIED) {
                throw new AppError('Pagamento recusado', HTTP_BAD_REQUEST);
            }

            const { userId, enrollmentId } = await db.transaction(async (tx) => {
                const userId = existingUser
                    ? existingUser.id
                    : await userModel.create({ name, email, password }, tx)
                        .catch(failWith('Erro ao criar usuário'));

                const enrollmentId = await enrollmentModel.create({ userId, courseId }, tx)
                    .catch(failWith('Erro Matrícula'));

                await paymentModel.create({ enrollmentId, amount: course.price, status }, tx)
                    .catch(failWith('Erro Pagamento'));

                await auditLogModel.create(`Checkout curso ${courseId} por ${userId}`, tx)
                    .catch(failWith('Erro DB'));

                return { userId, enrollmentId };
            });

            logger.info(`Checkout concluído: usuário ${userId}, curso "${course.title}"`);
            return { enrollmentId };
        }
    };
}

module.exports = createCheckoutService;
