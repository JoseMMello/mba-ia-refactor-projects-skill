================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
code-smells-project/
├── app.py                      # entry point: create_app(), routes, error handlers
├── config/
│   └── settings.py             # all settings, read from the environment
├── database.py                 # per-request connection, schema, seed
├── models/
│   ├── produto_model.py
│   ├── usuario_model.py        # password hashing and verification
│   ├── pedido_model.py         # order transaction, joined order listing
│   └── manutencao_model.py     # reset of all tables in one transaction
├── services/
│   ├── pedido_service.py       # stock check, total, notifications
│   └── relatorio_service.py    # discount tiers, sales report
├── controllers/
│   ├── produto_controller.py
│   ├── usuario_controller.py
│   ├── pedido_controller.py
│   ├── relatorio_controller.py
│   ├── health_controller.py    # / and /health
│   ├── admin_controller.py
│   └── validators.py
├── routes/
│   ├── __init__.py             # register_routes(app)
│   ├── produto_routes.py
│   ├── usuario_routes.py
│   ├── pedido_routes.py
│   ├── relatorio_routes.py
│   ├── health_routes.py
│   └── admin_routes.py
├── middlewares/
│   ├── error_handler.py        # AppError and the central handlers
│   └── auth.py                 # require_admin (X-Admin-Token)
├── .env.example
├── README.md
├── requirements.txt            # unchanged
└── loja.db                     # unchanged

Removed: controllers.py, models.py (code moved to the packages above)

## Findings Resolved
32 of 32

## Validation
  ok   Application boots without errors
  ok   All endpoints respond correctly (18 of 19; the 19th, POST /admin/query, was removed on purpose and now returns 404)
  ok   Zero anti-patterns remaining

## Behavior Changes
- POST /admin/query: removed (playbook T-04).
- POST /admin/reset-db: requires the X-Admin-Token header to match ADMIN_TOKEN; returns 403 otherwise, and is disabled when ADMIN_TOKEN is not set.
- GET /health: no longer returns secret_key, db_path or debug.
- GET /usuarios and GET /usuarios/<id>: no longer return senha.
- Passwords: new users and seeded users are stored hashed. Existing plain-text rows in loja.db are hashed on that user's next successful login.
- Seed users on a new database: their passwords come from SEED_ADMIN_PASSWORD and SEED_USER_PASSWORD. Without them they get a random password and cannot log in.
- Debug mode: off by default (DEBUG=true turns it on).
- Error bodies: every error is {"erro": ..., "sucesso": false}. Unexpected errors return "Erro interno do servidor" instead of the exception text. Unknown routes return JSON 404.
- Invalid input that used to return 500 now returns 400: missing or malformed JSON body, wrong field types, non-numeric preco_min/preco_max.
- New 400 cases: invalid e-mail format on POST /usuarios; order items without an integer produto_id and a quantidade greater than zero.
- PUT /produtos/<id>: now applies the same name length and category checks as POST /produtos.
================================
