const sqlite3 = require('sqlite3');
const config = require('../config');

function createExecutor(rawDb) {
    return {
        run(sql, params = []) {
            return new Promise((resolve, reject) => {
                rawDb.run(sql, params, function onRun(err) {
                    if (err) return reject(err);
                    resolve({ lastID: this.lastID, changes: this.changes });
                });
            });
        },
        get(sql, params = []) {
            return new Promise((resolve, reject) => {
                rawDb.get(sql, params, (err, row) => (err ? reject(err) : resolve(row)));
            });
        },
        all(sql, params = []) {
            return new Promise((resolve, reject) => {
                rawDb.all(sql, params, (err, rows) => (err ? reject(err) : resolve(rows)));
            });
        }
    };
}

// The application uses one connection, so every statement goes through a queue.
// This keeps statements of other requests out of an open transaction.
function createConnection() {
    const rawDb = new sqlite3.Database(config.databasePath);
    const executor = createExecutor(rawDb);
    let queue = Promise.resolve();

    function enqueue(work) {
        const result = queue.then(work);
        queue = result.catch(() => {});
        return result;
    }

    return {
        run: (sql, params) => enqueue(() => executor.run(sql, params)),
        get: (sql, params) => enqueue(() => executor.get(sql, params)),
        all: (sql, params) => enqueue(() => executor.all(sql, params)),

        // Runs `work` inside a transaction. `work` receives the executor to pass to the models.
        transaction(work) {
            return enqueue(async () => {
                await executor.run('BEGIN');
                try {
                    const result = await work(executor);
                    await executor.run('COMMIT');
                    return result;
                } catch (err) {
                    await executor.run('ROLLBACK').catch(() => {});
                    throw err;
                }
            });
        },

        close() {
            return enqueue(() => new Promise((resolve, reject) => {
                rawDb.close((err) => (err ? reject(err) : resolve()));
            }));
        }
    };
}

module.exports = { createConnection };
