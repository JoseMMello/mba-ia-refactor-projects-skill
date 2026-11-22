# Anti-Pattern Catalog

Knowledge for **Phase 2**. Check every source file against every entry below. An entry applies only when one of its detection signals is really present in the code. The fix for each entry is in `refactoring-playbook.md`, under the transformation named in "Fix".

## Severity scale

| Severity | Meaning |
|---|---|
| CRITICAL | Serious architecture or security failure: breaks correct behavior, exposes sensitive data, or removes any separation of responsibilities |
| HIGH | Strong violation of MVC or SOLID that makes maintenance and testing very hard |
| MEDIUM | Standardization problem, duplication, or moderate performance bottleneck |
| LOW | Readability, naming, magic numbers |

Use the severity given in each entry. Raise it one level only when the entry says so.

## CRITICAL

### AP-01 SQL Injection
- **Signals**: a query string built with `+`, `%`, `.format()`, f-strings or template literals that include a variable; `execute("..." + value)`; `` query(`... ${value}`) ``; raw user input passed as a whole query.
- **Not this**: queries with placeholders (`?`, `%s`, `$1`, `:name`) and the values passed separately.
- **Impact**: an attacker can read, change or delete any data, and bypass login.
- **Fix**: T-01 Parameterized queries.

### AP-02 Hardcoded Secrets and Credentials
- **Signals**: literal values assigned to names such as `SECRET_KEY`, `password`, `passwd`, `api_key`, `token`, `jwt_secret`; database URLs with user and password; payment or mail credentials in source; default admin passwords in seed code.
- **Impact**: anyone with access to the repository has the secrets, and they cannot change per environment.
- **Fix**: T-02 Configuration module.

### AP-03 Sensitive Data Exposure
- **Signals**: passwords stored or compared in plain text; password, token or secret fields returned in API responses; secrets or stack traces returned by health or debug endpoints; passwords or card numbers written to logs; weak hashing for passwords (`md5`, `sha1`, unsalted `sha256`).
- **Impact**: one leaked response or one database dump exposes every account.
- **Fix**: T-03 Password hashing and safe serialization.

### AP-04 Unprotected Dangerous Endpoint
- **Signals**: an endpoint that runs SQL or code received in the request; an endpoint that deletes or resets all data; admin, debug or financial operations with no authentication or authorization check; debug mode enabled for production (`debug=True`, `DEBUG = True`).
- **Impact**: any caller can destroy or take over the system.
- **Fix**: T-04 Remove or protect dangerous endpoints.

### AP-05 God Class / God File
- **Signals**: one file or class that mixes three or more of these: route registration, request handling, business rules, data access, configuration; one file serving several unrelated domains; a single class that creates the database, defines routes and holds the business logic.
- **Impact**: nothing can be tested in isolation, and any change can break everything.
- **Fix**: T-05 Split by layer and domain.

## HIGH

### AP-06 Business Logic or Data Access in the Wrong Layer
- **Signals**: SQL or ORM queries written inside route handlers; calculations, discounts, status rules or permission rules inside route handlers; models that read the HTTP request or build HTTP responses; route files with handlers longer than about 30 lines.
- **Impact**: rules cannot be reused or tested without HTTP, and each change touches several concerns.
- **Fix**: T-06 Thin routes, controllers and models.

### AP-07 Global Mutable State and Hard Coupling
- **Signals**: a module-level connection, cache or dictionary changed with `global` or reassigned from functions; state shared through module variables between requests; every module creating its own connection; dependencies created inside functions instead of being received.
- **Impact**: race conditions between requests, hidden dependencies, and code that cannot be tested with a fake dependency.
- **Fix**: T-07 Single database module and dependency injection.

### AP-08 No Centralized Error Handling
- **Signals**: the same `try/except` or `try/catch` block copied into every handler; raw exception text returned to the client (`str(e)`, `err.message`, stack traces); errors swallowed with an empty `except` or `catch`; inconsistent error formats between endpoints.
- **Impact**: internal details leak to clients, and errors are handled differently everywhere.
- **Fix**: T-08 Central error handler.

## MEDIUM

### AP-09 N+1 Queries
- **Signals**: a query executed inside a loop over the result of another query; a lazy-loaded relation accessed inside a loop; nested loops that each run a query.
- **Impact**: the number of queries grows with the data, so response time degrades as tables grow.
- **Fix**: T-09 Join or batch query.

### AP-10 Duplicated Code
- **Signals**: the same validation block in two or more handlers; the same row-to-dictionary mapping repeated; copies of the same function with small differences.
- **Impact**: a fix made in one copy is forgotten in the others.
- **Fix**: T-10 Extract shared function.

### AP-11 Missing or Weak Input Validation
- **Signals**: request fields used without checking presence or type; `request.get_json()` or `req.body` used with no check for a missing body; no format check on e-mail, dates or enumerated values; mass assignment of the request body to a model.
- **Impact**: bad data reaches the database, and requests fail with 500 instead of 400.
- **Fix**: T-11 Validation layer.

### AP-12 Deprecated APIs
- **Signals**: any use of an API in the table below, or any other API that the installed version of the language or framework marks as deprecated or removed.

| Stack | Deprecated | Modern equivalent |
|---|---|---|
| Python | `datetime.utcnow()`, `datetime.utcfromtimestamp()` | `datetime.now(timezone.utc)`, `datetime.fromtimestamp(ts, timezone.utc)` |
| SQLAlchemy | `Model.query.get(id)`, `query.get()` | `db.session.get(Model, id)` |
| Flask | `@app.before_first_request`, `FLASK_ENV`, `flask.json.JSONEncoder` | setup code in the app factory, `FLASK_DEBUG`, `app.json` provider |
| Node.js | `new Buffer(x)` | `Buffer.from(x)`, `Buffer.alloc(n)` |
| Node.js | `url.parse()` | `new URL()` |
| Node.js | `crypto.createCipher()` | `crypto.createCipheriv()` |
| Node.js | `fs.exists()` | `fs.existsSync()` or `fs.promises.access()` |
| JavaScript | `String.prototype.substr()` | `slice()` or `substring()` |
| Express | `body-parser` package for JSON | `express.json()`, `express.urlencoded()` |
| npm | `request` package | `fetch` (built in) |

- **Impact**: the code breaks or loses support on the next upgrade.
- **Fix**: T-12 Replace deprecated API.
- If no deprecated API is found, say so in the report summary instead of creating a finding.

### AP-13 Multi-step Write Without Transaction
- **Signals**: several inserts or updates that belong together (order and items, payment and enrollment, stock and sale) with no transaction, or with no rollback when a step fails.
- **Impact**: a failure in the middle leaves inconsistent data.
- **Fix**: T-13 Transaction.

## LOW

### AP-14 Magic Numbers and Strings
- **Signals**: unexplained numeric literals in rules (rates, limits, thresholds); status or category strings repeated in several places; ports and sizes written inline.
- **Impact**: the meaning is unclear, and a change must be made in several places.
- **Fix**: T-14 Named constants.

### AP-15 Print as Logging
- **Signals**: `print(...)` or `console.log(...)` used for application events or errors; fake notifications done with print.
- **Impact**: no levels, no control per environment, and sensitive data can end up in the output.
- **Fix**: T-15 Logger.

### AP-16 Poor Naming and Dead Code
- **Signals**: single-letter or meaningless names (`a`, `x1`, `data2`, `tmp`); names that shadow built-ins (`id`, `list`, `type`); unused imports, variables or functions; commented-out code.
- **Impact**: the code is harder to read, and dead code hides what is really used.
- **Fix**: T-16 Rename and remove.

## How to report

- One finding per anti-pattern per location. When the same anti-pattern appears in many places of one file, make one finding and list the lines (`models.py:28, 47-50, 109-111`).
- Give the exact file and line or line range. Confirm the numbers against the file before printing.
- Order findings from CRITICAL to LOW.
- A project with partial layers still has to be checked entry by entry. Folder names do not prove that a layer is respected.
