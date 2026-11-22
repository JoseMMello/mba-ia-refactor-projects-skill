const express = require('express');
const asyncHandler = require('../middlewares/asyncHandler');
const requireAdmin = require('../middlewares/requireAdmin');

function createUserRoutes(userController) {
    const router = express.Router();
    router.delete('/api/users/:id', requireAdmin, asyncHandler(userController.remove));
    return router;
}

module.exports = createUserRoutes;
