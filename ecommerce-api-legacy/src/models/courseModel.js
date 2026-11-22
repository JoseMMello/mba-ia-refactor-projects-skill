function createCourseModel(db) {
    return {
        async findActiveById(courseId, executor = db) {
            return executor.get('SELECT * FROM courses WHERE id = ? AND active = 1', [courseId]);
        },

        async create({ title, price, active }, executor = db) {
            const result = await executor.run(
                'INSERT INTO courses (title, price, active) VALUES (?, ?, ?)',
                [title, price, active]
            );
            return result.lastID;
        },

        async count(executor = db) {
            const row = await executor.get('SELECT COUNT(*) AS total FROM courses');
            return row.total;
        }
    };
}

module.exports = createCourseModel;
