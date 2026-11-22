```text
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
task-manager-api/
├── app.py                          # entry point: create_app(), registers blueprints and error handlers
├── database.py                     # SQLAlchemy instance (unchanged)
├── seed.py                         # seed in one transaction, passwords from configuration
├── requirements.txt                # unchanged
├── README.md                       # configuration notes added
├── .env.example                    # new: variable names, no values
├── config/
│   ├── __init__.py
│   └── settings.py                 # new: every setting and secret read from the environment
├── models/
│   ├── __init__.py
│   ├── category.py                 # + query methods, constants
│   ├── task.py                     # + query methods, constants, is_overdue() as the single overdue rule
│   └── user.py                     # salted password hash, to_dict() without password, query methods
├── controllers/                    # new: request flow of each domain
│   ├── __init__.py
│   ├── category_controller.py
│   ├── health_controller.py
│   ├── report_controller.py
│   ├── task_controller.py
│   ├── user_controller.py
│   └── validators/
│       ├── __init__.py
│       ├── category_validator.py
│       ├── common.py
│       ├── task_validator.py
│       └── user_validator.py
├── routes/                         # thin blueprints: path -> controller function
│   ├── __init__.py
│   ├── category_routes.py          # new: split out of report_routes.py
│   ├── health_routes.py            # new: / and /health moved out of app.py
│   ├── report_routes.py
│   ├── task_routes.py
│   └── user_routes.py
├── middlewares/                    # new
│   ├── __init__.py
│   ├── auth.py                     # require_admin (X-Admin-Token)
│   └── error_handler.py            # AppError + central JSON error handler
├── services/
│   ├── __init__.py
│   ├── notification_service.py     # SMTP settings from configuration, logger
│   └── report_service.py           # new: summary and user reports
└── utils/
    ├── __init__.py
    └── helpers.py                  # only the helpers in use (utc_now, parse_date, validators)

## Findings Resolved
50 of 51
Left open:
- [LOW] Poor Naming and Dead Code (AP-16), services/notification_service.py: the class is still not called by any endpoint. Its other findings were fixed (credentials moved to configuration, logger, deprecated API), but wiring it would make the API start sending e-mail, which is a new feature, and deleting it would remove the only notification code of the project. The owner has to choose.
Resolved with a limit:
- [CRITICAL] Unprotected Dangerous Endpoint (AP-04), user routes: the administrative user operations now require the admin token. `POST /login` still returns the placeholder `token` of the original API (`fake-jwt-token-<id>`), which no endpoint accepts; replacing it with real authentication is a new feature and was not done.
- [CRITICAL] Sensitive Data Exposure (AP-03): password hashes are now salted (werkzeug). Existing rows were handled by the seed, which rewrites the users; there is no migration on login, so a database created before the refactor must be seeded again (or have the passwords reset) before its users can log in.

## Validation
  ok Application boots without errors
  ok All endpoints respond correctly (22 of 22)
  fail Zero anti-patterns remaining (1 finding left open, listed above)

## Behavior Changes
- Password hashes are no longer returned: the `password` field was removed from the responses of `GET /users/<id>`, `POST /users`, `PUT /users/<id>` and from `user` in `POST /login`.
- `PUT /users/<id>` and `DELETE /users/<id>` now require the header `X-Admin-Token` equal to the `ADMIN_TOKEN` environment variable, and `POST /users` requires it when `role` is not `user`. Without the header, or while `ADMIN_TOKEN` is empty, they answer 403 `{"error": "Acesso negado"}`.
- Seed users no longer have fixed passwords: `seed.py` reads `SEED_ADMIN_PASSWORD`, `SEED_USER_PASSWORD` and `SEED_MANAGER_PASSWORD`, and generates a random password for each one that is empty.
- Debug mode is off unless `DEBUG=true`; host, port and database URL come from the environment with the original values as defaults (`0.0.0.0`, `5000`, `sqlite:///tasks.db`).
- Errors raised by the framework (404 for an unknown path, 405, 415 and 400 for a body that is not JSON) keep their status code but are now JSON `{"error": ...}` instead of an HTML page.
- Unexpected failures answer 500 `{"error": "Erro interno"}` on every endpoint; the specific 500 messages (`Erro ao criar task`, `Erro ao atualizar`, `Erro ao deletar`, `Erro ao criar usuário`, `Erro ao criar categoria`) are no longer used.
- Requests that used to fail with 500 now answer 400: non-integer `priority` or `user_id` in `GET /tasks/search`; `priority`, `title`, `description`, `tags`, `user_id` or `category_id` of the wrong type in `POST /tasks` and `PUT /tasks/<id>`; a body that is not a JSON object on any write endpoint.
- Stricter validation on values that were accepted before: `color` of a category must be `#RRGGBB`; `name` in `PUT /users/<id>` and in `PUT /categories/<id>` cannot be empty; `active` in `PUT /users/<id>` must be a boolean; `priority` must be an integer (a decimal such as 2.5 is refused).
================================
```
