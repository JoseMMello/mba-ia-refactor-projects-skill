function createEnrollmentModel(db) {
    return {
        async create({ userId, courseId }, executor = db) {
            const result = await executor.run(
                'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)',
                [userId, courseId]
            );
            return result.lastID;
        }
    };
}

module.exports = createEnrollmentModel;
