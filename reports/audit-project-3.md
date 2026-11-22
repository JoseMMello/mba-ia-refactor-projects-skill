```text
================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask 3.0.0
Files:   15 analyzed | ~1158 lines of code

## Summary
CRITICAL: 8 | HIGH: 6 | MEDIUM: 19 | LOW: 18
Deprecated APIs: 2 found (`datetime.utcnow()` in 9 files, `Model.query.get()` in 3 files)

## Findings

### [CRITICAL] Hardcoded Secrets and Credentials (AP-02)
File: app.py:13
Description: `app.config['SECRET_KEY']` is assigned a literal string in the source, next to the literal database URI on line 11.
Impact: Anyone with access to the repository knows the key that signs sessions, and it cannot change per environment.
Recommendation: Move `SECRET_KEY` and the database URI to a configuration module read from the environment (T-02), with a `.env.example` listing the names.

### [CRITICAL] Unprotected Dangerous Endpoint (AP-04)
File: app.py:34
Description: The application starts with `app.run(debug=True, host='0.0.0.0', port=5000)`, so the Werkzeug debugger is enabled while the server listens on every network interface.
Impact: The interactive debugger allows remote code execution to anyone who reaches the port, and it returns stack traces to clients.
Recommendation: Read the debug flag, host and port from configuration with debug off by default (T-04).

### [CRITICAL] Sensitive Data Exposure (AP-03)
File: models/user.py:21, 29, 32
Description: `to_dict()` includes the `password` field, and `set_password()` / `check_password()` hash passwords with unsalted `hashlib.md5`.
Impact: Every serialized user carries its password hash, and MD5 hashes are reversed in seconds, so one response or one database dump exposes every account.
Recommendation: Use a salted password hash and remove `password` from the serialization (T-03).

### [CRITICAL] God Class / God File (AP-05)
File: routes/report_routes.py:1-223
Description: One file serves two unrelated domains (reports on lines 12-155 and the whole category CRUD on lines 157-223) and mixes route registration, request handling, report calculations and ORM queries in the same functions; `summary_report` alone is 90 lines.
Impact: Category and report code cannot be changed or tested in isolation, and the category endpoints are hidden in a file named after reports.
Recommendation: Split by layer and domain (T-05): separate category and report routes, controllers and services.

### [CRITICAL] Sensitive Data Exposure (AP-03)
File: routes/user_routes.py:33, 85, 129, 209
Description: `GET /users/<id>`, `POST /users`, `PUT /users/<id>` and `POST /login` return `user.to_dict()`, which contains the stored password hash.
Impact: Any caller can collect the password hash of any user by id, with no authentication.
Recommendation: Return a serialization without the password field (T-03).

### [CRITICAL] Unprotected Dangerous Endpoint (AP-04)
File: routes/user_routes.py:52, 71-78, 119-122, 134-151, 210
Description: User administration has no authentication or authorization check: `POST /users` accepts `role: admin` from the body, `PUT /users/<id>` changes any user's role, password and `active` flag, and `DELETE /users/<id>` deletes any user with all their tasks. `POST /login` returns the fixed string `'fake-jwt-token-' + id`, which no endpoint ever checks.
Impact: Any caller can create an admin, take over an account or delete users and their data.
Recommendation: Protect the administrative user operations with an authentication and authorization check (T-04).

### [CRITICAL] Hardcoded Secrets and Credentials (AP-02)
File: seed.py:19, 26, 33
Description: The seed script creates the three default users, including the `admin` one on lines 17-20, with literal passwords passed to `set_password()`.
Impact: Every installation gets the same known admin credentials.
Recommendation: Read the seed passwords from the configuration module (T-02).

### [CRITICAL] Hardcoded Secrets and Credentials (AP-02)
File: services/notification_service.py:7-10
Description: The SMTP host, port, account (`email_user`) and its password (`email_password`) are literal values in `NotificationService.__init__`.
Impact: The mail account credentials are in the repository and cannot change per environment.
Recommendation: Read the SMTP settings from the configuration module (T-02).

### [HIGH] No Centralized Error Handling (AP-08)
File: routes/report_routes.py:186-188, 207-209, 221-223
Description: The three category write handlers repeat the same `try` / bare `except:` / `rollback` block and swallow the exception without logging it. The report handlers have no handling at all, so their errors return Flask's HTML 500 page.
Impact: The cause of a failure is lost, and clients get JSON errors on some endpoints and HTML on others.
Recommendation: Remove the copies and register one central error handler that logs and returns a JSON error (T-08).

### [HIGH] Business Logic or Data Access in the Wrong Layer (AP-06)
File: routes/task_routes.py:11-63, 85-154, 156-223, 240-271, 273-299
Description: The route handlers run the ORM queries, validate the fields, apply the overdue and completion-rate rules and build the responses. `get_tasks` has 53 lines, `create_task` 70 and `update_task` 68.
Impact: The task rules cannot be reused or tested without HTTP, and every change touches routing, rules and persistence together.
Recommendation: Keep the routes thin and move the rules to a service and the handling to a controller (T-06).

### [HIGH] No Centralized Error Handling (AP-08)
File: routes/task_routes.py:62-63, 137-138, 151-154, 204-205, 221-223, 236-238
Description: Each handler has its own `try/except`; four of them are bare `except:` that swallow any error, including the one around the whole of `get_tasks`. Unhandled errors (for example `int('abc')` on line 261) return Flask's HTML 500 page instead of JSON.
Impact: Errors are hidden, handled differently in each handler and returned in inconsistent formats.
Recommendation: Remove the copies and register one central error handler (T-08).

### [HIGH] Business Logic or Data Access in the Wrong Layer (AP-06)
File: routes/user_routes.py:10-25, 42-90, 92-132, 134-151, 153-183, 185-211
Description: The route handlers run the ORM queries, validate e-mail, password and role, apply the login rules (password check, inactive user) and delete the user's tasks. `create_user` has 49 lines and `update_user` 41.
Impact: The user and login rules cannot be reused or tested without HTTP.
Recommendation: Keep the routes thin and move the rules to a service and the handling to a controller (T-06).

### [HIGH] No Centralized Error Handling (AP-08)
File: routes/user_routes.py:87-90, 130-132, 149-151
Description: The three write handlers repeat the same `try/except` with `rollback`; two are bare `except:` that swallow the error.
Impact: The cause of a failure is lost and the handling is duplicated.
Recommendation: Remove the copies and register one central error handler (T-08).

### [HIGH] No Centralized Error Handling (AP-08)
File: utils/helpers.py:46, 49, 88
Description: `parse_date` and `process_task_data` use bare `except:` blocks that swallow every exception, including programming errors.
Impact: Real errors are turned into "invalid value" results with no trace.
Recommendation: Catch only the expected exception types and let the rest reach the central handler (T-08).

### [MEDIUM] Deprecated APIs (AP-12)
File: models/category.py:11
Description: The `created_at` column uses `datetime.utcnow` as default.
Impact: `datetime.utcnow()` is deprecated since Python 3.12 and emits a DeprecationWarning on the Python in use.
Recommendation: Replace with `datetime.now(timezone.utc)` (T-12).

### [MEDIUM] Deprecated APIs (AP-12)
File: models/task.py:15, 16, 52
Description: `created_at` and `updated_at` use `datetime.utcnow` as default and `onupdate`, and `is_overdue()` calls `datetime.utcnow()`.
Impact: The API is deprecated and scheduled for removal.
Recommendation: Replace with `datetime.now(timezone.utc)` (T-12).

### [MEDIUM] Deprecated APIs (AP-12)
File: models/user.py:14
Description: The `created_at` column uses `datetime.utcnow` as default.
Impact: The API is deprecated and scheduled for removal.
Recommendation: Replace with `datetime.now(timezone.utc)` (T-12).

### [MEDIUM] N+1 Queries (AP-09)
File: routes/report_routes.py:55-56, 161-163
Description: `summary_report` runs `Task.query.filter_by(user_id=u.id).all()` once per user inside the loop, and `get_categories` runs a `count()` query once per category.
Impact: The number of queries grows with the number of users and categories.
Recommendation: Replace with one grouped query for each case (T-09).

### [MEDIUM] Duplicated Code (AP-10)
File: routes/report_routes.py:19-22, 33-36, 132-135
Description: The overdue rule is written by hand twice in this file although `Task.is_overdue()` exists in `models/task.py:50`, and the count per status repeats `routes/task_routes.py:276-279`.
Impact: A change in the overdue rule or in the status list must be made in several copies.
Recommendation: Extract the shared rule and the status counting to one function (T-10).

### [MEDIUM] Missing or Weak Input Validation (AP-11)
File: routes/report_routes.py:179-180, 196-202
Description: `update_category` uses `request.get_json()` with no check for a missing body (`'name' in data` fails when the body is `null`) and assigns `name`, `description` and `color` with no type or presence check; `color` is never validated although the column has 7 characters.
Impact: Bad requests fail with 500 instead of 400, and empty names or invalid colors reach the database.
Recommendation: Validate the category payload in a validation layer (T-11).

### [MEDIUM] Deprecated APIs (AP-12)
File: routes/report_routes.py:35, 42, 45, 71, 105, 133, 192, 213
Description: `datetime.utcnow()` on lines 35, 42, 45, 71 and 133, and the legacy `Model.query.get()` on lines 105, 192 and 213.
Impact: `utcnow()` is deprecated in Python and `Query.get()` is legacy in SQLAlchemy 2.x.
Recommendation: Replace with `datetime.now(timezone.utc)` and `db.session.get(Model, id)` (T-12).

### [MEDIUM] N+1 Queries (AP-09)
File: routes/task_routes.py:41-57
Description: `get_tasks` runs `User.query.get(t.user_id)` and `Category.query.get(t.category_id)` for every task of the list.
Impact: Listing n tasks runs up to 2n extra queries.
Recommendation: Load the user and the category with the tasks in one query (T-09).

### [MEDIUM] Duplicated Code (AP-10)
File: routes/task_routes.py:17-28, 30-39, 71-80, 96-114, 166-184, 283-287
Description: Lines 17-28 copy `Task.to_dict()` field by field; the overdue rule is written three times instead of calling `Task.is_overdue()`; the title, status and priority validation of `create_task` is repeated in `update_task`.
Impact: A fix made in one copy is forgotten in the others (the two validations already return different messages for the same date error).
Recommendation: Extract the shared serialization, overdue rule and validation (T-10).

### [MEDIUM] Missing or Weak Input Validation (AP-11)
File: routes/task_routes.py:96, 113, 167, 182, 261, 264
Description: `title` and `priority` are used with no type check (`priority: "x"` raises TypeError on line 113, a `null` title raises on line 167), and the `priority` and `user_id` query parameters go straight into `int()` on lines 261 and 264.
Impact: Malformed requests return 500 instead of 400.
Recommendation: Validate types and formats in a validation layer (T-11).

### [MEDIUM] Deprecated APIs (AP-12)
File: routes/task_routes.py:31, 42, 51, 67, 72, 117, 122, 158, 188, 195, 215, 227, 285
Description: `datetime.utcnow()` on lines 31, 72, 215 and 285, and the legacy `Model.query.get()` on lines 42, 51, 67, 117, 122, 158, 188, 195 and 227.
Impact: `utcnow()` is deprecated in Python and `Query.get()` is legacy in SQLAlchemy 2.x.
Recommendation: Replace with `datetime.now(timezone.utc)` and `db.session.get(Model, id)` (T-12).

### [MEDIUM] N+1 Queries (AP-09)
File: routes/user_routes.py:22
Description: `get_users` reads the lazy relation `len(u.tasks)` inside the loop, which loads all the tasks of each user with one query per user only to count them.
Impact: Listing n users runs n extra queries and loads every task into memory.
Recommendation: Get the task count of all users with one grouped query (T-09).

### [MEDIUM] Duplicated Code (AP-10)
File: routes/user_routes.py:61, 106, 64, 115, 71, 120, 162-180
Description: The e-mail regular expression, the password length check and the role list are repeated in `create_user` and `update_user` (and a third copy of the regex is in `utils/helpers.py:21`); lines 162-180 are another copy of the task mapping and of the overdue rule.
Impact: A change in a rule must be made in every copy.
Recommendation: Extract shared validation and serialization functions (T-10).

### [MEDIUM] Missing or Weak Input Validation (AP-11)
File: routes/user_routes.py:64, 103, 115, 125
Description: `name` and `active` are assigned from the body in `update_user` with no type or presence check (a `null` name reaches the NOT NULL column), and `len(password)` is called with no check that the password is a string.
Impact: Bad data reaches the database or the request fails with 500 instead of 400.
Recommendation: Validate the user payload in a validation layer (T-11).

### [MEDIUM] Deprecated APIs (AP-12)
File: routes/user_routes.py:29, 94, 136, 155, 172
Description: The legacy `User.query.get()` on lines 29, 94, 136 and 155, and `datetime.utcnow()` on line 172.
Impact: `Query.get()` is legacy in SQLAlchemy 2.x and `utcnow()` is deprecated in Python.
Recommendation: Replace with `db.session.get(Model, id)` and `datetime.now(timezone.utc)` (T-12).

### [MEDIUM] Deprecated APIs (AP-12)
File: seed.py:66, 67, 69, 70, 74
Description: The due dates of the seed tasks are computed with `datetime.utcnow()`.
Impact: Running the seed prints DeprecationWarning and will break when the API is removed.
Recommendation: Replace with `datetime.now(timezone.utc)` (T-12).

### [MEDIUM] Multi-step Write Without Transaction (AP-13)
File: seed.py:11-14, 37, 63, 92
Description: The seed deletes every task, user and category and commits (line 14), then inserts users, categories and tasks in three more commits, with no rollback.
Impact: A failure after line 14 leaves the database empty or half populated.
Recommendation: Run the wipe and the inserts in one transaction with rollback (T-13).

### [MEDIUM] Deprecated APIs (AP-12)
File: services/notification_service.py:35
Description: The notification timestamp uses `datetime.utcnow()`.
Impact: The API is deprecated and scheduled for removal.
Recommendation: Replace with `datetime.now(timezone.utc)` (T-12).

### [MEDIUM] Deprecated APIs (AP-12)
File: utils/helpers.py:38
Description: `log_action` uses `datetime.utcnow()`.
Impact: The API is deprecated and scheduled for removal.
Recommendation: Replace with `datetime.now(timezone.utc)` (T-12).

### [LOW] Magic Numbers and Strings (AP-14)
File: app.py:11, 34
Description: The database URI, the host `'0.0.0.0'` and the port `5000` are written inline.
Impact: They cannot change per environment without editing the code.
Recommendation: Move them to named configuration values (T-14).

### [LOW] Poor Naming and Dead Code (AP-16)
File: app.py:7
Description: `os`, `sys` and `json` are imported and never used.
Impact: Dead imports hide what the module really depends on.
Recommendation: Remove the unused imports (T-16).

### [LOW] Poor Naming and Dead Code (AP-16)
File: models/category.py:14
Description: The dictionary built in `to_dict()` is named `d`.
Impact: Meaningless name.
Recommendation: Return the dictionary directly or give it a meaningful name (T-16).

### [LOW] Magic Numbers and Strings (AP-14)
File: models/task.py:39, 46, 53
Description: The status list, the priority limits `1` and `5` and the closed statuses `'done'` / `'cancelled'` are literals inside the methods.
Impact: The same values are repeated in the routes and in `utils/helpers.py`, so a change must be made in several places.
Recommendation: Use named constants defined once (T-14).

### [LOW] Poor Naming and Dead Code (AP-16)
File: models/task.py:3, 38-48, 50-60
Description: `json` is imported and never used; `validate_status()`, `validate_priority()` (with a parameter named `p`) and `is_overdue()` are never called.
Impact: Dead code suggests rules that the application does not really apply.
Recommendation: Remove the unused import and methods, or use them (T-16).

### [LOW] Poor Naming and Dead Code (AP-16)
File: models/user.py:34-38
Description: `is_admin()` is never called.
Impact: Dead code.
Recommendation: Use it in the authorization check or remove it (T-16).

### [LOW] Magic Numbers and Strings (AP-14)
File: routes/report_routes.py:19-28, 36, 45, 129, 134, 180
Description: Status strings and priority numbers are repeated as literals; `7` (days of recent activity), `2` (high priority threshold) and `'#000000'` (default color) are unexplained literals.
Impact: The meaning is unclear and the values are repeated.
Recommendation: Use named constants (T-14).

### [LOW] Poor Naming and Dead Code (AP-16)
File: routes/report_routes.py:7, 8
Description: `format_date`, `calculate_percentage` and `json` are imported and never used; loop variables are named `t`, `u`, `c`.
Impact: Dead imports and unclear names.
Recommendation: Remove the unused imports and rename (T-16).

### [LOW] Magic Numbers and Strings (AP-14)
File: routes/task_routes.py:32, 73, 96, 99, 104, 110, 113, 167, 169, 177, 182, 286
Description: The status list is written twice, the title limits `3` and `200` and the priority limits `1` and `5` twice each, the default priority `3` once, and `'done'` / `'cancelled'` three times, while the constants at `utils/helpers.py:110-116` are never used.
Impact: A change in a limit must be made in several places.
Recommendation: Use named constants defined once (T-14).

### [LOW] Print as Logging (AP-15)
File: routes/task_routes.py:149, 153, 219, 234
Description: Task events and the creation error are written with `print()`.
Impact: No levels and no control per environment.
Recommendation: Use the application logger (T-15).

### [LOW] Poor Naming and Dead Code (AP-16)
File: routes/task_routes.py:7, 221
Description: `json`, `os`, `sys` and `time` are imported and never used; the exception variable `e` on line 221 is never used; loop variables are named `t`.
Impact: Dead imports and unclear names.
Recommendation: Remove the unused imports and rename (T-16).

### [LOW] Magic Numbers and Strings (AP-14)
File: routes/user_routes.py:52, 64, 71, 115, 120, 173
Description: The minimum password length `4` and the role list are written twice each, and the default role and the closed statuses are literals.
Impact: A change must be made in several places.
Recommendation: Use named constants defined once (T-14).

### [LOW] Print as Logging (AP-15)
File: routes/user_routes.py:83, 89, 147
Description: User events and the creation error are written with `print()`.
Impact: No levels and no control per environment.
Recommendation: Use the application logger (T-15).

### [LOW] Poor Naming and Dead Code (AP-16)
File: routes/user_routes.py:6
Description: `hashlib` and `json` are imported and never used; loop variables are named `u` and `t`.
Impact: Dead imports and unclear names.
Recommendation: Remove the unused imports and rename (T-16).

### [LOW] Print as Logging (AP-15)
File: services/notification_service.py:21, 24
Description: The result and the failure of sending an e-mail are written with `print()`.
Impact: No levels, and the recipient address goes to standard output.
Recommendation: Use a logger (T-15).

### [LOW] Poor Naming and Dead Code (AP-16)
File: services/notification_service.py:1-48
Description: `NotificationService` is never imported or instantiated anywhere in the project.
Impact: The whole module is dead code that carries hardcoded credentials.
Recommendation: Wire it to the feature it was written for or remove it (T-16).

### [LOW] Print as Logging (AP-15)
File: utils/helpers.py:39, 41
Description: `log_action` writes to standard output with `print()`.
Impact: No levels and no control per environment.
Recommendation: Use a logger (T-15).

### [LOW] Poor Naming and Dead Code (AP-16)
File: utils/helpers.py:3-7, 9-116
Description: `os`, `json`, `sys`, `math` and `hashlib` are imported and never used, and no function or constant of this module is used by the application (the only import of it, at `routes/report_routes.py:7`, is itself unused). Parameters are named `s` and `p`.
Impact: The module looks like the validation layer but nothing runs through it.
Recommendation: Remove what stays unused and keep only what the refactored layers call (T-16).

================================
Total: 51 findings
================================
```
