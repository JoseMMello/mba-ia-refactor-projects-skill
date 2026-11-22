================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask 3.1.1
Files:   4 analyzed | ~780 lines of code

## Summary
CRITICAL: 11 | HIGH: 6 | MEDIUM: 7 | LOW: 8
Deprecated APIs: none found

## Findings

### [CRITICAL] SQL Injection (AP-01)
File: app.py:62, 69
Description: `executar_query` takes the `sql` field of the request body and passes it whole to `cursor.execute(query)`.
Impact: Any caller can read, change or delete any table.
Recommendation: Remove the endpoint or restrict it (T-04); no raw request text may reach `execute` (T-01).

### [CRITICAL] Hardcoded Secrets and Credentials (AP-02)
File: app.py:7
Description: `SECRET_KEY` is assigned a literal value in `app.config`.
Impact: Anyone with the repository has the key, and it cannot change per environment.
Recommendation: Read it from the environment in a configuration module (T-02) and add `.env.example`.

### [CRITICAL] Unprotected Dangerous Endpoint (AP-04)
File: app.py:8, 47-57, 59-78, 88
Description: `POST /admin/reset-db` deletes all rows of the four tables and `POST /admin/query` runs SQL from the request, both with no authentication. Debug mode is forced on (`DEBUG = True`, `debug=True`) with `host="0.0.0.0"`.
Impact: Any caller can wipe or take over the database, and the debugger is reachable from the network.
Recommendation: Remove or protect the admin endpoints and take debug and host from configuration (T-04).

### [CRITICAL] God Class / God File (AP-05)
File: app.py:6-9, 11-30, 47-78
Description: The entry point holds configuration, route registration, request handling and data access (`DELETE` statements and raw `execute`) in one file.
Impact: The entry point cannot be changed or tested without touching all four concerns.
Recommendation: Split by layer and domain (T-05), leaving only application bootstrap in app.py.

### [CRITICAL] Hardcoded Secrets and Credentials (AP-02)
File: controllers.py:289
Description: `health_check` contains a second literal copy of the secret key under `secret_key`.
Impact: The secret is duplicated in source and must be changed in two places.
Recommendation: Remove the literal; configuration is the only source (T-02).

### [CRITICAL] Sensitive Data Exposure (AP-03)
File: controllers.py:285-289
Description: `GET /health` returns `secret_key`, `db_path` and `debug` in the response body.
Impact: One unauthenticated request reveals the application secret and internal settings.
Recommendation: Return only status data from the health check (T-03).

### [CRITICAL] God Class / God File (AP-05)
File: controllers.py:5-292
Description: One file serves four unrelated domains (produtos, usuarios, pedidos, relatorios) plus health, and mixes request handling, validation rules and data access.
Impact: Every change to one domain touches a file shared by all the others.
Recommendation: Split into one controller per domain (T-05).

### [CRITICAL] Hardcoded Secrets and Credentials (AP-02)
File: database.py:75-79
Description: The seed inserts three users, including the `admin` account, with literal passwords.
Impact: Every fresh database ships with a known admin login.
Recommendation: Take the seed admin password from configuration and keep no password literal in source (T-02).

### [CRITICAL] SQL Injection (AP-01)
File: models.py:28, 47-50, 57-61, 68, 92, 109-111, 126-129, 140, 148-151, 155, 157-161, 163-166, 174, 188, 192, 220, 224, 279-281, 289-299
Description: Every query with input is built by concatenating values into the SQL string, including the login query in `login_usuario` and the filters in `buscar_produtos`.
Impact: An attacker can log in without a password and read or modify any table.
Recommendation: Use parameterized queries (T-01) in every data access function.

### [CRITICAL] Sensitive Data Exposure (AP-03)
File: models.py:83, 99, 109-111, 126-129
Description: `criar_usuario` stores `senha` in plain text, `login_usuario` compares it in plain text, and `get_todos_usuarios` and `get_usuario_por_id` return the `senha` field.
Impact: `GET /usuarios` exposes every account's password.
Recommendation: Hash passwords and remove `senha` from serialized users (T-03).

### [CRITICAL] God Class / God File (AP-05)
File: models.py:4-314
Description: One file holds data access for produtos, usuarios and pedidos together with business rules (order totals, stock checks, discount tiers).
Impact: Rules and queries for unrelated domains cannot be tested or changed in isolation.
Recommendation: Split into one model per domain and move the rules to services (T-05).

### [HIGH] Business Logic or Data Access in the Wrong Layer (AP-06)
File: app.py:49-55, 66-76
Description: The route handlers `reset_database` and `executar_query` open a cursor and run SQL directly.
Impact: Data access is tied to HTTP handlers in the entry point.
Recommendation: Thin routes, with data access in models (T-06).

### [HIGH] No Centralized Error Handling (AP-08)
File: app.py:77-78
Description: `executar_query` catches `Exception` and returns `str(e)` to the client.
Impact: Database error text leaks to callers.
Recommendation: Central error handler (T-08).

### [HIGH] Business Logic or Data Access in the Wrong Layer (AP-06)
File: controllers.py:28-54, 72-90, 208-210, 242, 247-250, 266-274
Description: Handlers hold product validation rules, the list of valid statuses, the notification steps, and four SQL queries in `health_check`.
Impact: The rules cannot be reused or tested without an HTTP request.
Recommendation: Move rules to services and queries to models (T-06).

### [HIGH] No Centralized Error Handling (AP-08)
File: controllers.py:10-12, 21-22, 60-62, 95-96, 108-109, 125-126, 133-134, 143-144, 164-165, 185-186, 218-220, 226-227, 234-235, 254-255, 261-262, 291-292
Description: The same `except Exception` block is copied into all 16 handlers and returns `str(e)`. Error bodies are inconsistent: some include `"sucesso": False` (20, 183, 206) and others do not.
Impact: Internal details leak, and clients cannot rely on one error format.
Recommendation: Central error handler with application exceptions (T-08).

### [HIGH] Global Mutable State and Hard Coupling (AP-07)
File: database.py:4-10
Description: `db_connection` is a module-level variable set through `global` and shared by all requests with `check_same_thread=False`. Every model function fetches it itself through `get_db()`.
Impact: Concurrent requests share one transaction, and nothing can be tested with a different database.
Recommendation: Single database module with a per-request connection (T-07).

### [HIGH] Business Logic or Data Access in the Wrong Layer (AP-06)
File: models.py:137-146, 256-262
Description: `criar_pedido` applies the stock rule and computes the order total; `relatorio_vendas` applies the discount tiers.
Impact: Business rules are mixed with SQL and cannot change independently.
Recommendation: Move the rules to services; models keep only data access (T-06).

### [MEDIUM] Missing or Weak Input Validation (AP-11)
File: app.py:61-62
Description: `executar_query` calls `dados.get` on the result of `request.get_json()` without checking for a missing body.
Impact: A request without a JSON body fails with 500.
Recommendation: Validation layer (T-11).

### [MEDIUM] Multi-step Write Without Transaction (AP-13)
File: app.py:51-55
Description: `reset_database` runs four `DELETE` statements with no rollback if one fails.
Impact: A failure can leave some tables emptied and others not, pending on the shared connection.
Recommendation: Transaction with rollback (T-13).

### [MEDIUM] Duplicated Code (AP-10)
File: controllers.py:28-46, 72-90
Description: `criar_produto` and `atualizar_produto` repeat the same required-field and negative-value checks, and the copies differ (update skips the name length and category checks at 47-54).
Impact: Updates can store values that creation rejects.
Recommendation: Extract one shared product validator (T-10).

### [MEDIUM] Missing or Weak Input Validation (AP-11)
File: controllers.py:43-50, 118-121, 153-158, 169-170, 195-201, 239-240
Description: `preco`, `estoque` and `nome` are compared with no type check; `preco_min` and `preco_max` go to `float()` unchecked; `email` has no format check; order `itens` are passed on with no check of `produto_id` or `quantidade`; `login` and `atualizar_status_pedido` call `.get` on a body that may be missing.
Impact: Bad input returns 500 instead of 400, and a negative `quantidade` creates a negative total and raises stock.
Recommendation: Validation layer (T-11).

### [MEDIUM] N+1 Queries (AP-09)
File: models.py:139-141, 154-156, 187-199, 219-231
Description: `get_pedidos_usuario` and `get_todos_pedidos` run one query per order for its items and one per item for the product name; `criar_pedido` queries each product twice inside loops.
Impact: The number of queries grows with orders times items.
Recommendation: Join or batch query (T-09).

### [MEDIUM] Duplicated Code (AP-10)
File: models.py:12-21, 31-40, 304-313, 79-86, 95-102, 171-201, 203-233
Description: The product row-to-dictionary mapping appears three times and the user mapping twice; `get_pedidos_usuario` and `get_todos_pedidos` are copies that differ only in the `WHERE` clause.
Impact: A change to one mapping or listing is easily missed in the copies.
Recommendation: Extract shared mappers and one order query (T-10).

### [MEDIUM] Multi-step Write Without Transaction (AP-13)
File: models.py:148-168
Description: `criar_pedido` inserts the order, inserts each item and updates stock with no rollback when a step fails.
Impact: A failure in the middle leaves an order without items, or stock out of step, to be committed by the next request on the shared connection.
Recommendation: Transaction with rollback (T-13).

### [LOW] Magic Numbers and Strings (AP-14)
File: app.py:36, 85, 88
Description: The version string `"1.0.0"` and the port `5000` are written inline, the port twice.
Impact: The values must be changed in several places.
Recommendation: Named constants and configuration (T-14).

### [LOW] Print as Logging (AP-15)
File: app.py:56, 83-86
Description: `print` is used for the database reset event and the startup banner.
Impact: No levels and no control per environment.
Recommendation: Logger (T-15).

### [LOW] Magic Numbers and Strings (AP-14)
File: controllers.py:47-50, 52, 242, 285-286
Description: The name length limits `2` and `200`, the category list, the status list, and the `"1.0.0"` and `"producao"` strings are inline literals.
Impact: The same values are repeated and their meaning is not named.
Recommendation: Named constants (T-14).

### [LOW] Print as Logging (AP-15)
File: controllers.py:8, 11, 57, 61, 106, 161, 179, 182, 208-210, 219, 248, 250
Description: `print` is used for events and errors, for fake e-mail, SMS and push notifications, and it writes user e-mails to the output at 161, 179 and 182.
Impact: No levels, and personal data ends up in the output.
Recommendation: Logger (T-15).

### [LOW] Poor Naming and Dead Code (AP-16)
File: controllers.py:14, 56, 64, 98, 136, 160
Description: The name `id` shadows the built-in, as a parameter and as a local variable.
Impact: The built-in is hidden inside those functions and the name says nothing about which entity it is.
Recommendation: Rename to `produto_id` and `usuario_id` (T-16).

### [LOW] Poor Naming and Dead Code (AP-16)
File: database.py:2
Description: `import os` is never used.
Impact: Dead code hides what the module really depends on.
Recommendation: Remove (T-16).

### [LOW] Magic Numbers and Strings (AP-14)
File: models.py:150, 247, 250, 253, 257-262
Description: The discount thresholds `10000`, `5000`, `1000` and rates `0.1`, `0.05`, `0.02` are unexplained literals, and the status strings `'pendente'`, `'aprovado'`, `'cancelado'` are repeated here and in controllers.py.
Impact: The rule is unclear, and a status rename must be made in several places.
Recommendation: Named constants (T-14).

### [LOW] Poor Naming and Dead Code (AP-16)
File: models.py:2, 24, 54, 65, 89
Description: `import sqlite3` is never used, and four functions take a parameter named `id`, shadowing the built-in.
Impact: Dead import and unclear names.
Recommendation: Rename and remove (T-16).

================================
Total: 32 findings
================================
