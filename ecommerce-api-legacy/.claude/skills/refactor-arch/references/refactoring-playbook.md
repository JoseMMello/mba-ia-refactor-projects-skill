# Refactoring Playbook

Knowledge for **Phase 3**. One transformation for each anti-pattern in `anti-patterns.md`. The examples alternate between Python and JavaScript to show the idea. Apply the same idea with the syntax and libraries of the project's stack, and use the names found in the project, not the names in these examples.

## T-01 Parameterized queries (fixes AP-01)

Replace every value concatenated into a query with a placeholder, and pass the values separately.

Before:
```python
cursor.execute("SELECT * FROM users WHERE email = '" + email + "' AND active = " + str(active))
```
After:
```python
cursor.execute("SELECT * FROM users WHERE email = ? AND active = ?", (email, active))
```

Before:
```javascript
db.all(`SELECT * FROM courses WHERE title LIKE '%${term}%'`, callback);
```
After:
```javascript
db.all('SELECT * FROM courses WHERE title LIKE ?', [`%${term}%`], callback);
```

Use the placeholder style of the driver (`?`, `%s`, `$1`). Table and column names cannot be placeholders: choose them from a fixed list in the code.

## T-02 Configuration module (fixes AP-02)

Move every secret and setting to one config module that reads the environment. Add `.env.example` with the names only.

Before:
```python
app.config["SECRET_KEY"] = "my-secret-123"
app.run(port=5000, debug=True)
```
After:
```python
# config/settings.py
import os

class Settings:
    SECRET_KEY = os.environ.get("SECRET_KEY", "")
    DATABASE_PATH = os.environ.get("DATABASE_PATH", "app.db")
    PORT = int(os.environ.get("PORT", "5000"))
    DEBUG = os.environ.get("DEBUG", "false").lower() == "true"

settings = Settings()
```
```python
# app.py
from config.settings import settings

app.config["SECRET_KEY"] = settings.SECRET_KEY
app.run(port=settings.PORT, debug=settings.DEBUG)
```

Keep the original port and database path as the defaults so the application still starts the same way. Never write a real secret as a default.

## T-03 Password hashing and safe serialization (fixes AP-03)

Hash passwords on write, verify the hash on login, and never serialize sensitive fields.

Before:
```python
cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))

def to_dict(row):
    return {"id": row["id"], "email": row["email"], "password": row["password"]}
```
After:
```python
from werkzeug.security import generate_password_hash, check_password_hash

cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)",
               (email, generate_password_hash(password)))

def to_dict(row):
    return {"id": row["id"], "email": row["email"]}

def verify(row, password):
    return check_password_hash(row["password"], password)
```

Use a hashing library that the stack already provides (`werkzeug.security` with Flask, `crypto.scrypt` in Node.js) before adding a dependency. Replace `md5` or `sha1` password hashing the same way. Existing rows with plain-text or weak hashes: hash them in the seed code, or migrate them on the next successful login, and say which one was done. Remove secrets and internal paths from health and debug responses.

## T-04 Remove or protect dangerous endpoints (fixes AP-04)

An endpoint that executes SQL or code from the request has no safe form: remove it and report the removal under "Behavior Changes". For destructive or administrative endpoints, require authorization and disable them outside development.

Before:
```javascript
app.post('/admin/reset', (req, res) => {
  db.run('DELETE FROM orders');
  res.json({ ok: true });
});
```
After:
```javascript
// middlewares/requireAdmin.js
const config = require('../config');

module.exports = function requireAdmin(req, res, next) {
  if (!config.adminToken || req.get('x-admin-token') !== config.adminToken) {
    return res.status(403).json({ error: 'Forbidden' });
  }
  next();
};

// routes/adminRoutes.js
router.post('/admin/reset', requireAdmin, adminController.reset);
```

Take debug mode from configuration, off by default.

## T-05 Split by layer and domain (fixes AP-05)

Break the god file into models, controllers and routes, one file per domain entity, following `mvc-guidelines.md`.

Before (one file):
```javascript
class Server {
  constructor() { this.db = new sqlite3.Database(':memory:'); }
  initDb() { /* CREATE TABLE ... */ }
  setupRoutes(app) {
    app.post('/checkout', (req, res) => { /* validation + rules + SQL */ });
    app.get('/report', (req, res) => { /* SQL + formatting */ });
  }
}
```
After:
```
src/
├── app.js                       # creates the app, registers routes and error handler
├── config/index.js
├── database/connection.js       # creates the connection and the schema
├── models/orderModel.js         # queries for orders
├── controllers/checkoutController.js   # flow of the checkout request
├── routes/checkoutRoutes.js     # POST /checkout -> checkoutController.checkout
└── middlewares/errorHandler.js
```

Move one domain at a time and start the application after each move.

## T-06 Thin routes, controllers and models (fixes AP-06)

Move queries to the model, keep the flow in the controller, and leave only the mapping in the route.

Before:
```python
@app.route("/orders/<int:order_id>/total")
def order_total(order_id):
    rows = db.execute("SELECT price, quantity FROM items WHERE order_id = ?", (order_id,)).fetchall()
    total = sum(r["price"] * r["quantity"] for r in rows)
    if total > 1000:
        total = total * 0.9
    return jsonify({"total": total})
```
After:
```python
# models/order_model.py
BULK_DISCOUNT_THRESHOLD = 1000
BULK_DISCOUNT_RATE = 0.10

def get_items(order_id):
    return get_db().execute(
        "SELECT price, quantity FROM items WHERE order_id = ?", (order_id,)).fetchall()

def calculate_total(items):
    total = sum(i["price"] * i["quantity"] for i in items)
    if total > BULK_DISCOUNT_THRESHOLD:
        total = total * (1 - BULK_DISCOUNT_RATE)
    return total

# controllers/order_controller.py
def order_total(order_id):
    items = order_model.get_items(order_id)
    return jsonify({"total": order_model.calculate_total(items)})

# routes/order_routes.py
orders_bp.add_url_rule("/orders/<int:order_id>/total", view_func=order_controller.order_total)
```

## T-07 Single database module and dependency injection (fixes AP-07)

Create the connection in one place and hand it to whoever needs it, instead of global variables changed from several modules.

Before:
```javascript
let db = null;
let cache = {};
function getUsers() {
  if (!db) db = new sqlite3.Database('app.db');
  /* ... */
}
```
After:
```javascript
// database/connection.js
const sqlite3 = require('sqlite3');
const config = require('../config');

function createConnection() {
  return new sqlite3.Database(config.databasePath);
}
module.exports = { createConnection };

// models/userModel.js
module.exports = (db) => ({
  findAll(callback) { db.all('SELECT id, name, email FROM users', callback); },
});

// app.js (composition root)
const db = createConnection();
const userModel = require('./models/userModel')(db);
const userController = require('./controllers/userController')(userModel);
```

In Flask, keep the connection per request (`flask.g` with a teardown function) or use the extension's session, created in the app factory.

## T-08 Central error handler (fixes AP-08)

Remove the repeated `try/except` blocks and register one handler that returns a consistent error body without internal details.

Before:
```python
def list_products():
    try:
        return jsonify(product_model.find_all()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```
After:
```python
# middlewares/error_handler.py
import logging
from flask import jsonify
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)

class AppError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.message = message
        self.status = status

def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(error):
        return jsonify({"error": error.message}), error.status

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        return jsonify({"error": error.description}), error.code

    @app.errorhandler(Exception)
    def handle_unexpected(error):
        logger.exception("Unhandled error")
        return jsonify({"error": "Internal server error"}), 500

# controllers/product_controller.py
def list_products():
    return jsonify(product_model.find_all()), 200
```

In Express, the equivalent is one `app.use((err, req, res, next) => ...)` registered after the routes, with handlers calling `next(err)`. Keep the error body keys that the original API used, so clients do not break.

## T-09 Join or batch query (fixes AP-09)

Replace the query inside the loop with one joined query, or one `IN (...)` query, and group the rows in memory.

Before:
```python
orders = db.execute("SELECT * FROM orders").fetchall()
for order in orders:
    items = db.execute("SELECT * FROM items WHERE order_id = ?", (order["id"],)).fetchall()
```
After:
```python
rows = db.execute("""
    SELECT o.id AS order_id, o.status, i.product_id, i.quantity
    FROM orders o
    LEFT JOIN items i ON i.order_id = o.id
    ORDER BY o.id
""").fetchall()

orders = {}
for row in rows:
    order = orders.setdefault(row["order_id"], {"id": row["order_id"], "status": row["status"], "items": []})
    if row["product_id"] is not None:
        order["items"].append({"product_id": row["product_id"], "quantity": row["quantity"]})
result = list(orders.values())
```

With an ORM, use eager loading (`joinedload`, `include`). The response must keep the same shape as before.

## T-10 Extract shared function (fixes AP-10)

Before:
```javascript
// in create
if (!body.name || body.name.length < 2) return res.status(400).json({ error: 'Invalid name' });
if (body.price < 0) return res.status(400).json({ error: 'Invalid price' });
// in update: the same lines again
```
After:
```javascript
// controllers/validators/productValidator.js
function validateProduct(body) {
  if (!body || !body.name || body.name.length < 2) return 'Invalid name';
  if (typeof body.price !== 'number' || body.price < 0) return 'Invalid price';
  return null;
}
module.exports = { validateProduct };

// in create and in update
const error = validateProduct(req.body);
if (error) return res.status(400).json({ error });
```

Do the same for repeated row-to-object mapping: one `to_dict` or serializer per entity.

## T-11 Validation layer (fixes AP-11)

Validate presence, type and format before the data reaches the model, and answer 400 instead of failing with 500.

Before:
```python
def create_user():
    data = request.get_json()
    user_model.create(data["name"], data["email"], data["password"])
```
After:
```python
import re

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD_LENGTH = 8

def validate_user(data):
    if not isinstance(data, dict):
        raise AppError("Invalid body")
    for field in ("name", "email", "password"):
        if not isinstance(data.get(field), str) or not data[field].strip():
            raise AppError(f"{field} is required")
    if not EMAIL_PATTERN.match(data["email"]):
        raise AppError("Invalid email")
    if len(data["password"]) < MIN_PASSWORD_LENGTH:
        raise AppError("Password too short")

def create_user():
    data = request.get_json(silent=True)
    validate_user(data)
    user_id = user_model.create(data["name"], data["email"], data["password"])
    return jsonify({"id": user_id}), 201
```

Keep the validation messages and status codes that the original API already returned for the same cases.

## T-12 Replace deprecated API (fixes AP-12)

Use the table in `anti-patterns.md` (AP-12) to pick the modern equivalent.

Before:
```python
from datetime import datetime
created_at = datetime.utcnow()
user = User.query.get(user_id)
```
After:
```python
from datetime import datetime, timezone
created_at = datetime.now(timezone.utc)
user = db.session.get(User, user_id)
```

Before:
```javascript
const bodyParser = require('body-parser');
app.use(bodyParser.json());
const token = new Buffer(text).toString('base64');
```
After:
```javascript
app.use(express.json());
const token = Buffer.from(text).toString('base64');
```

Remove a dependency from the manifest when its replacement is built in. Check that stored or returned date formats do not change.

## T-13 Transaction (fixes AP-13)

Group the writes that belong together, commit once, and roll back on failure.

Before:
```python
cursor.execute("INSERT INTO orders (user_id, total) VALUES (?, ?)", (user_id, total))
order_id = cursor.lastrowid
for item in items:
    cursor.execute("INSERT INTO items (order_id, product_id) VALUES (?, ?)", (order_id, item["product_id"]))
    cursor.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (item["quantity"], item["product_id"]))
db.commit()
```
After:
```python
try:
    cursor.execute("INSERT INTO orders (user_id, total) VALUES (?, ?)", (user_id, total))
    order_id = cursor.lastrowid
    for item in items:
        cursor.execute("INSERT INTO items (order_id, product_id) VALUES (?, ?)", (order_id, item["product_id"]))
        cursor.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (item["quantity"], item["product_id"]))
    db.commit()
except Exception:
    db.rollback()
    raise
```

## T-14 Named constants (fixes AP-14)

Before:
```javascript
if (total > 10000) discount = total * 0.1;
if (!['pending', 'approved', 'cancelled'].includes(status)) return res.status(400).end();
```
After:
```javascript
const HIGH_VALUE_THRESHOLD = 10000;
const HIGH_VALUE_DISCOUNT_RATE = 0.1;
const ORDER_STATUSES = ['pending', 'approved', 'cancelled'];

if (total > HIGH_VALUE_THRESHOLD) discount = total * HIGH_VALUE_DISCOUNT_RATE;
if (!ORDER_STATUSES.includes(status)) return res.status(400).end();
```

Put constants next to the rule they belong to (the model or a constants module), not in the config module, which is for values that change per environment.

## T-15 Logger (fixes AP-15)

Before:
```python
print("ERROR creating order: " + str(e))
print("Login ok: " + email + " password " + password)
```
After:
```python
import logging
logger = logging.getLogger(__name__)

logger.exception("Error creating order")
logger.info("Login ok for user id %s", user_id)
```

Configure the logging level once, in the entry point, from configuration. Never log passwords, tokens or card numbers. In Node.js, use one small logger module (or the logging library the project already has) instead of scattered `console.log`.

## T-16 Rename and remove (fixes AP-16)

Before:
```python
import sqlite3, os, sys   # os and sys unused

def get(id):
    x = find(id)
    # old = find_old(id)
    return x
```
After:
```python
import sqlite3

def get_product(product_id):
    return find_product(product_id)
```

Keep URL parameter names when the framework binds them by name, or update the route at the same time.

## Order of work

1. T-02 and T-07 first: config and database modules are the base for everything else.
2. T-05 and T-06: create the structure and move the code, one domain at a time.
3. T-01, T-03, T-04: security fixes inside the new models and controllers.
4. T-08, T-11, T-10: error handling, validation, duplication.
5. T-09, T-12, T-13: performance, deprecated APIs, transactions.
6. T-14, T-15, T-16: readability.

Start the application after each step. A step that breaks the boot is fixed before the next one begins.
