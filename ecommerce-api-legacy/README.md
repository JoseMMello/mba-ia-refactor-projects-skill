# ecommerce-api-legacy

LMS API (com fluxo de checkout) em Node.js/Express usada como entrada do desafio `refactor-arch`.

## Como rodar

```bash
npm install
npm start
```

A aplicação sobe em `http://localhost:3000`. O banco SQLite é em memória e já carrega seeds automaticamente no boot.

Exemplos de requisições estão em `api.http`.

## Configuração

A configuração é lida de variáveis de ambiente. Para desenvolvimento, copie `.env.example` para `.env` e preencha os valores (o arquivo `.env` é carregado automaticamente no boot).

| Variável | Para que serve | Padrão |
|---|---|---|
| `PORT` | Porta HTTP | `3000` |
| `DATABASE_PATH` | Caminho do banco SQLite | `:memory:` |
| `LOG_LEVEL` | Nível de log (`debug`, `info`, `warn`, `error`) | `info` |
| `ADMIN_TOKEN` | Token exigido pelas rotas administrativas | vazio (rotas respondem 403) |
| `PAYMENT_GATEWAY_KEY` | Chave do gateway de pagamento | vazio |
| `SEED_USER_PASSWORD` | Senha do usuário criado pelo seed | vazio (senha aleatória) |

## Rotas

| Método | Rota | Acesso |
|---|---|---|
| `POST` | `/api/checkout` | público |
| `GET` | `/api/admin/financial-report` | header `x-admin-token` |
| `DELETE` | `/api/users/:id` | header `x-admin-token` |

## Estrutura

```
src/
├── app.js            # ponto de entrada: monta as dependências e sobe o servidor
├── config/           # configuração lida do ambiente
├── database/         # conexão, schema e seed
├── models/           # consultas e regras dos dados
├── services/         # fluxo de checkout e pagamento
├── controllers/      # fluxo de cada requisição e validação
├── routes/           # mapeamento de método e caminho
├── middlewares/      # autenticação de admin e tratamento central de erros
├── errors/           # erro de aplicação
└── logger.js
```
