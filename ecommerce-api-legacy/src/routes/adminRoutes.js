const express = require('express');
const asyncHandler = require('../middlewares/asyncHandler');
const requireAdmin = require('../middlewares/requireAdmin');

function createAdminRoutes(adminController) {
    const router = express.Router();
    router.get('/api/admin/financial-report', requireAdmin, asyncHandler(adminController.financialReport));
    return router;
}

module.exports = createAdminRoutes;
