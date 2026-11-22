# task-manager-api

API de Task Manager em Python/Flask usada como entrada do desafio `refactor-arch`. Diferente dos outros projetos, este já possui alguma separação de camadas (`models/`, `routes/`, `services/`, `utils/`), mas ainda contém problemas arquiteturais e de qualidade.

## Como rodar

```bash
pip install -r requirements.txt
python seed.py
python app.py
```

Configuração (opcional): copie `.env.example` para `.env` e preencha. Sem `.env` a aplicação sobe com os padrões (porta 5000, SQLite `tasks.db`, debug desligado).

- `SEED_ADMIN_PASSWORD`, `SEED_USER_PASSWORD`, `SEED_MANAGER_PASSWORD`: senhas dos usuários criados pelo `seed.py`. Se ficarem vazias o seed gera senhas aleatórias e não é possível fazer login com esses usuários.
- `ADMIN_TOKEN`: token exigido no header `X-Admin-Token` em `PUT /users/<id>`, `DELETE /users/<id>` e em `POST /users` com `role` diferente de `user`. Vazio = essas operações respondem 403.
- `PORT`, `HOST`, `DEBUG`, `DATABASE_URL`, `SECRET_KEY`, `LOG_LEVEL`: ver `.env.example`.

A aplicação sobe em `http://localhost:5000`. O `seed.py` popula o banco SQLite (`tasks.db`) com usuários, categorias e tasks de exemplo — **rode-o antes do primeiro boot**, caso contrário os endpoints vão retornar listas vazias.
