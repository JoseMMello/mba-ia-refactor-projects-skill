function createAuditLogModel(db) {
    return {
        async create(action, executor = db) {
            const result = await executor.run(
                "INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))",
                [action]
            );
            return result.lastID;
        }
    };
}

module.exports = createAuditLogModel;
