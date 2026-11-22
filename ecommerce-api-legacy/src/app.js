const express = require('express');
const config = require('./config');
const logger = require('./logger');
const { createConnection } = require('./database/connection');
const { createSchema } = require('./database/schema');
const { seedDatabase } = require('./database/seed');
const createUserModel = require('./models/userModel');
const createCourseModel = require('./models/courseModel');
const createEnrollmentModel = require('./models/enrollmentModel');
const createPaymentModel = require('./models/paymentModel');
const createAuditLogModel = require('./models/auditLogModel');
const createFinancialReportModel = require('./models/financialReportModel');
const createPaymentService = require('./services/paymentService');
const createCheckoutService = require('./services/checkoutService');
const createCheckoutController = require('./controllers/checkoutController');
const createAdminController = require('./controllers/adminController');
const createUserController = require('./controllers/userController');
const createCheckoutRoutes = require('./routes/checkoutRoutes');
const createAdminRoutes = require('./routes/adminRoutes');
const createUserRoutes = require('./routes/userRoutes');
const errorHandler = require('./middlewares/errorHandler');

async function start() {
    const db = createConnection();

    const userModel = createUserModel(db);
    const courseModel = createCourseModel(db);
    const enrollmentModel = createEnrollmentModel(db);
    const paymentModel = createPaymentModel(db);
    const auditLogModel = createAuditLogModel(db);
    const financialReportModel = createFinancialReportModel(db);

    await createSchema(db);
    await seedDatabase({ db, userModel, courseModel, enrollmentModel, paymentModel });

    const paymentService = createPaymentService({ gatewayKey: config.paymentGatewayKey, logger });
    const checkoutService = createCheckoutService({
        db, courseModel, userModel, enrollmentModel, paymentModel, auditLogModel, paymentService, logger
    });

    const app = express();
    app.use(express.json());
    app.use(createCheckoutRoutes(createCheckoutController(checkoutService)));
    app.use(createAdminRoutes(createAdminController(financialReportModel)));
    app.use(createUserRoutes(createUserController(userModel)));
    app.use(errorHandler);

    if (!config.adminToken) {
        logger.warn('ADMIN_TOKEN não configurado: as rotas administrativas respondem 403');
    }

    app.listen(config.port, () => {
        logger.info(`Frankenstein LMS rodando na porta ${config.port}...`);
    });
}

start().catch((err) => {
    logger.error('Falha ao iniciar a aplicação', err);
    process.exit(1);
});
