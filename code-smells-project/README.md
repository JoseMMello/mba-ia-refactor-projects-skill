# code-smells-project

API de E-commerce em Python/Flask usada como entrada do desafio `refactor-arch`.

## Como rodar

```bash
pip install -r requirements.txt
python app.py
```

A aplicação sobe em `http://localhost:5001`. O banco SQLite (`loja.db`) é criado automaticamente no primeiro boot, já com produtos e usuários de exemplo.

## Configuração

Toda a configuração vem de variáveis de ambiente, listadas em `.env.example`. Nenhuma é obrigatória para subir a aplicação. Para usar um arquivo `.env`:

```bash
cp .env.example .env
set -a; source .env; set +a
python app.py
```

- `SEED_ADMIN_PASSWORD` e `SEED_USER_PASSWORD`: senhas dos usuários de exemplo criados em um banco novo. Sem elas, esses usuários recebem uma senha aleatória e não conseguem fazer login.
- `ADMIN_TOKEN`: exigido no cabeçalho `X-Admin-Token` por `POST /admin/reset-db`. Sem ele, a rota fica desabilitada.
- `DEBUG`: desligado por padrão.

## Estrutura

```
app.py              ponto de entrada
config/             configuração lida do ambiente
database.py         conexão por requisição, schema e seed
models/             acesso a dados, um arquivo por entidade
services/           regras que envolvem mais de um model
controllers/        fluxo de cada requisição e validação
routes/             mapeamento de método e caminho (blueprints)
middlewares/        tratamento central de erros e autorização de admin
```
