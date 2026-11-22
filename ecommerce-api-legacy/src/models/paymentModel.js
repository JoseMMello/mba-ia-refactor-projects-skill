function createPaymentModel(db) {
    return {
        async create({ enrollmentId, amount, status }, executor = db) {
            const result = await executor.run(
                'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)',
                [enrollmentId, amount, status]
            );
            return result.lastID;
        }
    };
}

module.exports = createPaymentModel;
