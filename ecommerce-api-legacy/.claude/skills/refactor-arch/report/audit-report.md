================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   JavaScript (Node.js) + Express ^4.18.2
Files:   3 analyzed | ~180 lines of code

## Summary
CRITICAL: 6 | HIGH: 4 | MEDIUM: 3 | LOW: 7
Deprecated APIs: none found

## Findings

### [CRITICAL] Hardcoded Secrets and Credentials (AP-02)
File: src/AppManager.js:18, 68
Description: The seed inserts the user 'leonan@fullcycle.com.br' with a literal password written in the SQL string (line 18), and the checkout falls back to a literal default password when `pwd` is not sent (line 68).
Impact: Anyone who reads the repository knows the password of the seeded account and the password given to every user created without `pwd`.
Recommendation: Move the seed password to configuration read from the environment and remove the default password, requiring `pwd` when a new user is created (T-02).

### [CRITICAL] Sensitive Data Exposure (AP-03)
File: src/AppManager.js:18, 45, 68
Description: The seeded user password is stored in plain text (line 18); the full card number `cc` and `config.paymentGatewayKey` are written to the log on every checkout (line 45); new passwords are stored with `badCrypto`, which is not a password hash (line 68).
Impact: The application log exposes card numbers and the payment gateway key, and a database dump exposes the passwords.
Recommendation: Hash every password, including the seeded one, with a salted password hash, and never log the card number or the gateway key (T-03).

### [CRITICAL] Unprotected Dangerous Endpoint (AP-04)
File: src/AppManager.js:80-129, 131-137
Description: `GET /api/admin/financial-report` returns revenue and student names, and `DELETE /api/users/:id` deletes any user, both with no authentication or authorization check.
Impact: Any caller can read the financial data and delete every user account.
Recommendation: Protect both routes with an authentication middleware that checks an admin credential read from the environment (T-04).

### [CRITICAL] God Class / God File (AP-05)
File: src/AppManager.js:4-139
Description: The class `AppManager` creates the database connection (line 7), creates the schema and the seed (lines 10-23), registers the three routes (lines 25-138) and holds the request handling, the payment and enrollment rules and all the SQL, for the unrelated domains of checkout, financial report and users.
Impact: Nothing can be tested in isolation, and any change to one domain can break the others.
Recommendation: Split the class by layer and domain into config, database, models, services, controllers and routes (T-05).

### [CRITICAL] Hardcoded Secrets and Credentials (AP-02)
File: src/utils.js:2-5
Description: The `config` object holds literal values for `dbUser`, `dbPass`, `paymentGatewayKey` and `smtpUser` in source code.
Impact: Anyone with access to the repository has the database password and the live payment gateway key, and they cannot change per environment.
Recommendation: Move the values to a configuration module that reads them from the environment, with a `.env.example` listing the variable names (T-02).

### [CRITICAL] Sensitive Data Exposure (AP-03)
File: src/utils.js:17-23
Description: `badCrypto` builds the stored password value by repeating the first two characters of the base64 encoding of the password and cutting the result to 10 characters, with no salt and no hash function.
Impact: The stored value depends only on the first characters of the password, so different passwords collide and the value can be reversed.
Recommendation: Replace `badCrypto` with a salted password hash from the standard library (T-03).

### [HIGH] Business Logic or Data Access in the Wrong Layer (AP-06)
File: src/AppManager.js:28-78, 80-129, 131-137
Description: The three route handlers run SQL directly (lines 37, 40, 50, 54, 57, 69, 83, 92, 104, 106, 133) and hold business rules: the payment approval rule (line 46) and the revenue calculation (lines 108-110). The checkout handler has 51 lines and the report handler has 50.
Impact: The rules cannot be reused or tested without HTTP, and each change touches routing, rules and data access together.
Recommendation: Keep routes thin, move request handling to controllers, rules to services and SQL to models (T-06).

### [HIGH] Global Mutable State and Hard Coupling (AP-07)
File: src/AppManager.js:7
Description: The constructor creates the `sqlite3.Database` connection itself instead of receiving it, and every query reaches it through `this.db`.
Impact: The data access cannot be tested with a fake or temporary database, and the dependency is hidden inside the class.
Recommendation: Create the connection in a single database module and inject it into the models (T-07).

### [HIGH] No Centralized Error Handling (AP-08)
File: src/AppManager.js:38, 57, 92, 104, 106, 133
Description: There is no error handler. Database errors are ignored in the callbacks of lines 57, 92, 104, 106 and 133 (line 93 then reads `enrollments.length` of an undefined value, and line 135 reports success even when the delete failed); line 38 answers 404 for a database error; errors are sent as plain text (lines 35, 38, 41, 48, 51, 55, 70, 84) while successes are sent as JSON.
Impact: A database error crashes the process or is reported as success, and the client receives inconsistent error formats.
Recommendation: Add a central error-handling middleware and application error classes, and forward every error to it (T-08).

### [HIGH] Global Mutable State and Hard Coupling (AP-07)
File: src/utils.js:9-15, 25
Description: `globalCache` is a module-level object changed by `logAndCache` on every checkout and never cleared, and `totalRevenue` is a module-level variable exported by value (line 25).
Impact: State is shared between requests and grows without limit, and the exported `totalRevenue` can never reflect a change.
Recommendation: Remove the module-level state; keep per-request data inside the service that owns it (T-07).

### [MEDIUM] N+1 Queries (AP-09)
File: src/AppManager.js:89-127
Description: The financial report runs one query for the enrollments of each course (line 92) and, for each enrollment, one query for the user (line 104) and one for the payment (line 106), inside nested `forEach` loops.
Impact: The number of queries grows with courses and enrollments, so the report gets slower as the tables grow.
Recommendation: Read the report with a single query that joins courses, enrollments, users and payments (T-09).

### [MEDIUM] Missing or Weak Input Validation (AP-11)
File: src/AppManager.js:29-35, 46, 132
Description: The checkout only checks that `usr`, `eml`, `c_id` and `card` are present (line 35): there is no type or format check, `pwd` is optional, and `cc.startsWith` (line 46) throws when `card` is sent as a number. `req.params.id` is used without validation (line 132).
Impact: A request with a numeric `card` raises an uncaught exception inside a database callback, and bad data reaches the database.
Recommendation: Add a validation layer for the checkout body and for the `id` parameter that answers 400 (T-11).

### [MEDIUM] Multi-step Write Without Transaction (AP-13)
File: src/AppManager.js:50-62, 69-72
Description: The checkout inserts the user (line 69), the enrollment (line 50), the payment (line 54) and the audit log (line 57) as separate statements with no transaction and no rollback.
Impact: A failure in the payment insert leaves an enrollment with no payment, and a refused payment leaves the new user created.
Recommendation: Run the user, enrollment, payment and audit log inserts inside one transaction with rollback on failure (T-13).

### [LOW] Magic Numbers and Strings (AP-14)
File: src/AppManager.js:46, 48, 68, 108
Description: The card prefix `"4"` that approves a payment (line 46) and the default password literal (line 68) are unexplained, and the status strings `"PAID"` and `"DENIED"` are repeated in lines 46, 48 and 108.
Impact: The meaning of the values is unclear, and a status change must be made in several places.
Recommendation: Replace the literals with named constants (T-14).

### [LOW] Print as Logging (AP-15)
File: src/AppManager.js:45
Description: `console.log` is used to record the payment processing event.
Impact: There are no log levels and no control per environment, and sensitive data ends up in the output.
Recommendation: Use a logger module with levels (T-15).

### [LOW] Poor Naming and Dead Code (AP-16)
File: src/AppManager.js:2, 29-33, 89
Description: `totalRevenue` is imported and never used (line 2); the checkout fields are held in the variables `u`, `e`, `p`, `cid` and `cc` (lines 29-33), and the course of the report loop is named `c` (line 89).
Impact: The code is harder to read, and the unused import hides what is really used.
Recommendation: Rename the variables to meaningful names and remove the unused import (T-16).

### [LOW] Print as Logging (AP-15)
File: src/app.js:13
Description: `console.log` is used to record the application start.
Impact: There are no log levels and no control per environment.
Recommendation: Use a logger module with levels (T-15).

### [LOW] Magic Numbers and Strings (AP-14)
File: src/utils.js:19-22
Description: `badCrypto` uses the unexplained literals `10000` (loop count), `2` and `10` (cut lengths).
Impact: The meaning of the numbers is unclear.
Recommendation: Remove them with the function, or name them as constants (T-14).

### [LOW] Print as Logging (AP-15)
File: src/utils.js:13
Description: `logAndCache` uses `console.log` to record each cache write.
Impact: There are no log levels and no control per environment.
Recommendation: Use a logger module with levels (T-15).

### [LOW] Poor Naming and Dead Code (AP-16)
File: src/utils.js:2, 3, 5, 9-10
Description: `config.dbUser`, `config.dbPass` and `config.smtpUser` are never read, `globalCache` is written and never read, and `totalRevenue` is never used.
Impact: Dead code hides what is really used and keeps unused secrets in the source.
Recommendation: Remove the unused values and variables (T-16).

================================
Total: 20 findings
================================
