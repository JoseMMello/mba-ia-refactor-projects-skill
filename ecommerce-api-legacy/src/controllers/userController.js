const { validateId } = require('./validators/idValidator');

function createUserController(userModel) {
    return {
        async remove(req, res) {
            const userId = validateId(req.params.id);
            await userModel.deleteById(userId);
            res.send('Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco.');
        }
    };
}

module.exports = createUserController;
