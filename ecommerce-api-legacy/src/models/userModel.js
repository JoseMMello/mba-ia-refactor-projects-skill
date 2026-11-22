const crypto = require('crypto');
const { promisify } = require('util');

const scrypt = promisify(crypto.scrypt);

const HASH_ALGORITHM = 'scrypt';
const SALT_BYTES = 16;
const KEY_BYTES = 64;

// Stored format: scrypt$<salt in hex>$<derived key in hex>
async function hashPassword(password) {
    const salt = crypto.randomBytes(SALT_BYTES);
    const key = await scrypt(password, salt, KEY_BYTES);
    return `${HASH_ALGORITHM}$${salt.toString('hex')}$${key.toString('hex')}`;
}

function createUserModel(db) {
    return {
        async findByEmail(email, executor = db) {
            return executor.get('SELECT id FROM users WHERE email = ?', [email]);
        },

        async create({ name, email, password }, executor = db) {
            const passwordHash = await hashPassword(password);
            const result = await executor.run(
                'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
                [name, email, passwordHash]
            );
            return result.lastID;
        },

        async deleteById(userId, executor = db) {
            await executor.run('DELETE FROM users WHERE id = ?', [userId]);
        },

        async count(executor = db) {
            const row = await executor.get('SELECT COUNT(*) AS total FROM users');
            return row.total;
        }
    };
}

module.exports = createUserModel;
