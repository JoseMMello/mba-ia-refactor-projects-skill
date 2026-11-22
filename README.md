# refactor-arch: skill de auditoria e refatoração arquitetural

Desafio técnico do MBA em Engenharia de Software com IA (Full Cycle), módulo Desenvolvimento de Software e Aplicações com IA.

A skill `refactor-arch` analisa um projeto de backend, audita o código contra um catálogo de anti-patterns, gera um relatório e refatora o projeto para MVC, validando que a aplicação continua funcionando. A mesma pasta da skill foi usada, sem alteração, em três projetos: dois em Python/Flask e um em Node.js/Express.

| Projeto | Stack | Findings | Endpoints após a refatoração |
|---|---|---|---|
| `code-smells-project` | Python + Flask | 32 | 18 de 19 respondem (1 removido de propósito) |
| `ecommerce-api-legacy` | Node.js + Express | 20 | 3 de 3 |
| `task-manager-api` | Python + Flask | 51 | 22 de 22 |

Ferramenta usada: Claude Code, com Custom Skills.

## Estrutura do repositório

```
├── code-smells-project/       # Projeto 1, refatorado
│   └── .claude/skills/refactor-arch/
│       ├── SKILL.md
│       ├── references/        # os 5 arquivos de conhecimento
│       └── report/            # saída da skill neste projeto
├── ecommerce-api-legacy/      # Projeto 2, refatorado (mesma skill)
├── task-manager-api/          # Projeto 3, refatorado (mesma skill)
└── reports/
    ├── audit-project-1.md
    ├── audit-project-2.md
    └── audit-project-3.md
```

O código original dos três projetos está no primeiro commit do repositório (`6d1ce62`), para comparação.

---

## A) Análise Manual

Feita lendo o código original, antes de escrever a skill. As linhas se referem ao código do commit inicial.

### Projeto 1: code-smells-project (Python/Flask, API de e-commerce)

| Severidade | Problema | Onde | Por que importa |
|---|---|---|---|
| CRITICAL | SQL injection: todas as queries são montadas por concatenação, inclusive a do login | `models.py:28`, `47-50`, `109-111`, `291` | Permite ler ou apagar qualquer tabela e entrar sem senha |
| CRITICAL | `/admin/query` executa qualquer SQL recebido e `/admin/reset-db` apaga o banco, os dois sem autenticação | `app.py:47-78` | Qualquer chamada externa toma ou destrói o sistema |
| CRITICAL | `SECRET_KEY` fixa no código e devolvida pelo `/health` | `app.py:7`, `controllers.py:289` | O segredo fica no repositório e é exposto por um endpoint público |
| CRITICAL | Senhas em texto puro, devolvidas por `GET /usuarios` | `database.py:75-79`, `models.py:83`, `99` | Um vazamento de resposta ou de banco expõe todas as contas |
| HIGH | Um arquivo com queries, regras de negócio e formatação de 4 domínios | `models.py:1-314` | Nada pode ser testado isolado; qualquer mudança afeta tudo |
| HIGH | Conexão global mutável compartilhada entre threads | `database.py:4-10` | Condição de corrida entre requisições e dependência escondida |
| MEDIUM | Queries N+1: uma query por pedido e outra por item | `models.py:187-193`, `219-225` | O tempo de resposta cresce com o volume de dados |
| MEDIUM | Validação duplicada entre criar e atualizar produto | `controllers.py:28-46`, `72-90` | Uma correção feita em uma cópia é esquecida na outra |
| MEDIUM | Sem tratamento central de erros; cada handler repete `try/except` e devolve o texto da exceção | `controllers.py:10-12` e demais handlers | Vaza detalhes internos e deixa os erros inconsistentes |
| LOW | Números mágicos na regra de desconto | `models.py:257-262` | O significado dos valores não está no código |
| LOW | `print` usado como log, inclusive simulando envio de e-mail e SMS | `controllers.py:8`, `208-210` | Sem níveis e sem controle por ambiente |
| LOW | Import não usado e `id` sobrescrevendo um builtin | `models.py:2`, `24` | Ruído e risco de confusão na leitura |

### Projeto 2: ecommerce-api-legacy (Node.js/Express, LMS com checkout)

| Severidade | Problema | Onde | Por que importa |
|---|---|---|---|
| CRITICAL | Credenciais de banco, chave do gateway de pagamento e usuário SMTP fixos no código | `src/utils.js:1-7` | Segredos de produção ficam no repositório |
| CRITICAL | Número do cartão e chave do gateway escritos no log | `src/AppManager.js:45` | Dado de cartão em log é vazamento e viola PCI |
| CRITICAL | "Criptografia" de senha caseira e senha padrão `123456` para usuário novo | `src/utils.js:17-23`, `src/AppManager.js:68` | O hash é reversível na prática e a senha padrão é conhecida |
| CRITICAL | Relatório financeiro e exclusão de usuário sem autenticação | `src/AppManager.js:80`, `131` | Qualquer chamada lê o faturamento ou apaga usuários |
| CRITICAL | God Class: cria o banco, registra rotas e contém regras e SQL | `src/AppManager.js:4-139` | Sem separação de responsabilidades; impossível testar em partes |
| HIGH | Estado global mutável (`globalCache`, `totalRevenue`) | `src/utils.js:9-10` | Estado compartilhado entre requisições, sem controle |
| MEDIUM | N+1 no relatório: uma query por curso, por matrícula, por usuário e por pagamento | `src/AppManager.js:89-106` | O número de queries cresce com os dados |
| MEDIUM | Checkout grava usuário, matrícula, pagamento e log sem transação | `src/AppManager.js:50-57`, `69` | Uma falha no meio deixa dados inconsistentes |
| MEDIUM | Erros de banco ignorados nos callbacks; exclusão responde sucesso mesmo com erro | `src/AppManager.js:92`, `104`, `106`, `133` | Falhas passam despercebidas |
| LOW | Nomes sem significado (`u`, `e`, `p`, `cid`, `cc`) | `src/AppManager.js:29-33` | Dificulta a leitura do fluxo principal |
| LOW | Strings mágicas `PAID` e `DENIED` e regra do cartão que começa com 4 | `src/AppManager.js:46`, `108` | A regra não tem nome e se repete |
| LOW | `console.log` como log e import não usado (`totalRevenue`) | `src/AppManager.js:2`, `45`; `src/utils.js:13` | Sem níveis de log; código morto |

### Projeto 3: task-manager-api (Python/Flask, já com camadas parciais)

| Severidade | Problema | Onde | Por que importa |
|---|---|---|---|
| CRITICAL | `SECRET_KEY` fixa e credenciais SMTP no código | `app.py:13`, `services/notification_service.py:7-10` | Segredos no repositório |
| CRITICAL | Senha com MD5 sem salt | `models/user.py:29`, `32` | MD5 é quebrado em segundos com tabelas prontas |
| CRITICAL | Hash da senha devolvido nas respostas de usuário e no login | `models/user.py:21`, `routes/user_routes.py:209` | Expõe o hash de todas as contas |
| CRITICAL | Nenhuma rota exige autenticação; o login devolve um token falso | `routes/user_routes.py:92`, `134`, `210` | Qualquer um altera ou apaga usuários |
| HIGH | Rotas com queries, validação e regras de negócio; `services/` e `utils/` existem, mas quase não são usados | `routes/task_routes.py:11-62`, `routes/report_routes.py:12-100` | As pastas sugerem camadas que o código não respeita |
| MEDIUM | N+1: usuário e categoria buscados por task; tasks buscadas por usuário | `routes/task_routes.py:42`, `51`; `routes/report_routes.py:55-56`, `163` | Degrada com o volume de dados |
| MEDIUM | APIs deprecated: `datetime.utcnow()` e `Model.query.get()` | `models/task.py:15-16`, `routes/task_routes.py:67` e outros | Quebram ou perdem suporte nas próximas versões |
| MEDIUM | `except:` genérico engolindo erros | `routes/task_routes.py:62`, `routes/user_routes.py:130`, `utils/helpers.py:46` | Esconde a causa das falhas |
| MEDIUM | Validação duplicada entre as rotas e `process_task_data`, que nunca é chamada | `routes/task_routes.py:99`, `169`; `utils/helpers.py:57-108` | Duas versões da mesma regra, uma delas morta |
| LOW | Imports não usados | `app.py:7`, `utils/helpers.py:3-7`, `routes/task_routes.py:7` | Ruído |
| LOW | `print` como log | `routes/user_routes.py:83`, `utils/helpers.py:39` | Sem níveis e sem controle |
| LOW | Números mágicos de validação (200, 4, 1 a 5) repetidos, com constantes equivalentes não usadas | `routes/task_routes.py:99`, `113`; `routes/user_routes.py:64` | A mesma regra escrita em vários lugares |

---

## B) Construção da Skill

### Decisões de design

A skill separa processo de conhecimento:

- **`SKILL.md`** tem só o processo: as três fases em ordem, o que ler em cada uma, o que imprimir, quando parar e como validar. É um roteiro numerado e curto.
- **`references/`** tem o conhecimento. Nenhum arquivo é carregado sozinho: cada fase do `SKILL.md` cita pelo caminho o arquivo que deve ser lido.

| Arquivo | Área de conhecimento | Usado na |
|---|---|---|
| `references/project-analysis.md` | Heurísticas de detecção de linguagem, framework, banco, ponto de entrada, endpoints e arquitetura atual; formato do resumo da Fase 1 | Fase 1 |
| `references/anti-patterns.md` | Catálogo de 16 anti-patterns com sinais de detecção, severidade e impacto | Fase 2 |
| `references/report-template.md` | Formato do relatório de auditoria | Fase 2 |
| `references/mvc-guidelines.md` | Camadas, direção das dependências, estrutura alvo e regras do MVC | Fase 3 |
| `references/refactoring-playbook.md` | 16 transformações com código antes e depois, e a ordem de trabalho | Fase 3 |

Outras decisões:

- **Cada anti-pattern tem um código (`AP-01` a `AP-16`) e aponta para uma transformação (`T-01` a `T-16`).** É o que liga a auditoria à refatoração: o relatório cita o `AP`, e a Fase 3 sabe qual `T` aplicar.
- **A pausa é uma regra explícita.** A Fase 2 termina com a pergunta `Proceed with refactoring (Phase 3)? [y/n]` e a instrução de não alterar nenhum arquivo do projeto antes da resposta.
- **A skill salva as próprias saídas.** O relatório vai para `report/audit-report.md` e o resumo da Fase 3 para `report/refactor-summary.md`, dentro da pasta da skill. Um caminho passado como argumento (`/refactor-arch ../reports/audit-project-1.md`) substitui o local padrão.
- **A validação faz parte da Fase 3.** A skill sobe a aplicação, chama todos os endpoints do inventário da Fase 1 e procura de novo os anti-patterns reportados. Ela só imprime o resumo final quando a aplicação sobe.
- **Os arquivos da skill são somente leitura** durante a execução. Só os dois arquivos de saída são escritos.

### Anti-patterns do catálogo

| Severidade | Anti-patterns |
|---|---|
| CRITICAL | AP-01 SQL Injection · AP-02 Hardcoded Secrets · AP-03 Sensitive Data Exposure · AP-04 Unprotected Dangerous Endpoint · AP-05 God Class / God File |
| HIGH | AP-06 Business Logic or Data Access in the Wrong Layer · AP-07 Global Mutable State · AP-08 No Centralized Error Handling |
| MEDIUM | AP-09 N+1 Queries · AP-10 Duplicated Code · AP-11 Missing Input Validation · AP-12 Deprecated APIs · AP-13 Multi-step Write Without Transaction |
| LOW | AP-14 Magic Numbers and Strings · AP-15 Print as Logging · AP-16 Poor Naming and Dead Code |

Os anti-patterns vieram da análise manual: cada problema encontrado nos três projetos virou uma entrada genérica, descrita por sinais que dá para verificar no código (por exemplo, "query montada com `+`, `%`, `.format()` ou template literal"), e não por nomes dos projetos. O AP-12 tem uma tabela de APIs obsoletas com o equivalente moderno para Python, SQLAlchemy, Flask, Node.js e Express.

### Como a skill ficou agnóstica de tecnologia

- Nenhum arquivo cita nomes de arquivos, tabelas ou rotas dos três projetos.
- As heurísticas de detecção são tabelas de sinal para conclusão que cobrem várias stacks (Python, Node.js, Java, Go, PHP, Ruby, C#).
- O playbook alterna exemplos em Python e JavaScript e manda aplicar a ideia com a sintaxe do projeto.
- As guidelines descrevem as camadas e dão a estrutura alvo em Python e em Node.js, com a regra de adaptar ao ponto de partida: projeto sem camadas ganha a estrutura completa, e projeto com camadas parciais mantém o que está certo.
- A prova foi a execução: a mesma pasta rodou nos três projetos.

### Desafios encontrados

| Desafio | Como foi resolvido |
|---|---|
| O primeiro arquivo de referência era um prompt de agente completo, que proibia modificar arquivos e dar recomendações | Reescrito como referência: só heurísticas e o formato de saída, sem persona nem regras de processo |
| Salvar o relatório antes da confirmação contradizia a regra "não crie nenhum arquivo antes da confirmação" | A regra passou a falar em arquivos do projeto, com o relatório como única exceção |
| A porta 5000 estava ocupada na máquina (AirPlay do macOS) e a skill mudou a porta padrão do projeto 1 para 5001 | Regra nova na validação: usar outra porta só para validar, sem mudar o padrão do projeto. O projeto 1 ficou com 5001 como padrão, configurável por `PORT` |
| Um endpoint que executa SQL recebido na requisição não tem versão segura | O playbook manda remover e registrar em "Behavior Changes". É o único endpoint original que deixou de responder |
| "Um finding por local" não dizia o que é local, e os totais variavam conforme a leitura | Definido no catálogo: local é arquivo. O mesmo anti-pattern em dois arquivos são dois findings |
| AP-05 e AP-06 se sobrepunham nos arquivos de rota | Critério de desempate no catálogo: AP-05 para o arquivo que concentra a aplicação ou domínios sem relação; AP-06 para o arquivo de uma camada fazendo o trabalho de outra |
| "Resposta de erro JSON consistente" conflitava com "manter o formato original" no projeto que responde texto puro | Regra ajustada: consistente quer dizer um único lugar monta os erros, no formato que a API já usa |
| A troca de `datetime.utcnow()` por um datetime com timezone mudaria o formato das datas | Nota no playbook: remover o timezone depois de ler o relógio, em um único helper |
| Um modelo local menor contou 16 rotas onde havia 19, porque o projeto mistura dois estilos de registro | Instrução explícita de somar as rotas de todos os estilos |

As seis últimas correções foram feitas depois das execuções. Os relatórios em `reports/` são a saída das execuções reais, anteriores a esses ajustes de texto.

---

## C) Resultados

### Findings por severidade

| Projeto | CRITICAL | HIGH | MEDIUM | LOW | Total | APIs deprecated |
|---|---|---|---|---|---|---|
| 1. code-smells-project | 11 | 6 | 7 | 8 | 32 | nenhuma |
| 2. ecommerce-api-legacy | 6 | 4 | 3 | 7 | 20 | nenhuma |
| 3. task-manager-api | 8 | 6 | 19 | 18 | 51 | 2 (`datetime.utcnow()`, `Model.query.get()`) |

Relatórios completos: [`reports/audit-project-1.md`](reports/audit-project-1.md), [`reports/audit-project-2.md`](reports/audit-project-2.md), [`reports/audit-project-3.md`](reports/audit-project-3.md).

A auditoria encontrou todos os problemas da análise manual do projeto 1 e os principais dos projetos 2 e 3. O total do projeto 3 é alto porque o mesmo anti-pattern aparece em vários arquivos: só o AP-12 gerou 9 findings para 2 APIs.

### Estrutura antes e depois

**Projeto 1: code-smells-project**

```
ANTES                      DEPOIS
├── app.py                 ├── app.py                  # create_app(), composition root
├── controllers.py         ├── config/settings.py      # configuração lida do ambiente
├── models.py              ├── database.py             # conexão por requisição, schema, seed
├── database.py            ├── models/                 # produto, usuario, pedido, manutencao
└── requirements.txt       ├── services/               # pedido, relatorio
                           ├── controllers/            # um por domínio + validators
                           ├── routes/                 # um blueprint por domínio
                           ├── middlewares/            # error_handler, auth
                           ├── .env.example
                           └── requirements.txt
```

**Projeto 2: ecommerce-api-legacy**

```
ANTES                      DEPOIS
└── src/                   └── src/
    ├── app.js                 ├── app.js              # composition root
    ├── AppManager.js          ├── logger.js
    └── utils.js               ├── config/index.js
                               ├── database/           # connection, schema, seed
                               ├── errors/AppError.js
                               ├── models/             # user, course, enrollment, payment, auditLog, financialReport
                               ├── services/           # checkout, payment
                               ├── controllers/        # admin, checkout, user + validators
                               ├── routes/             # admin, checkout, user
                               └── middlewares/        # asyncHandler, errorHandler, requireAdmin
```

**Projeto 3: task-manager-api**

```
ANTES                      DEPOIS
├── app.py                 ├── app.py                  # create_app()
├── database.py            ├── database.py             # sem alteração
├── seed.py                ├── seed.py                 # uma transação, senhas da configuração
├── models/                ├── config/settings.py      # novo
├── routes/                ├── models/                 # mesmos arquivos, com queries e hash com salt
├── services/              ├── controllers/            # novo: fluxo de cada domínio + validators
└── utils/                 ├── routes/                 # blueprints finos; category e health separados
                           ├── middlewares/            # novo: auth, error_handler
                           ├── services/               # notification + report_service
                           ├── utils/helpers.py        # só os helpers em uso
                           └── .env.example
```

No projeto 3 a skill manteve as pastas e os nomes que já existiam e acrescentou só o que faltava (controllers, config, middlewares), como pede a regra de adaptação.

### Checklist de validação

| Item | Projeto 1 | Projeto 2 | Projeto 3 |
|---|---|---|---|
| **Fase 1** | | | |
| Linguagem detectada corretamente | [x] Python | [x] JavaScript (Node.js) | [x] Python |
| Framework detectado corretamente | [x] Flask 3.1.1 | [x] Express ^4.18.2 | [x] Flask 3.0.0 |
| Domínio descrito corretamente | [x] E-commerce | [x] LMS com checkout | [x] Task manager |
| Número de arquivos condiz com a realidade | [x] 4 | [x] 3 | [x] 15 |
| **Fase 2** | | | |
| Relatório segue o template | [x] | [x] | [x] |
| Cada finding tem arquivo e linhas exatos | [x] | [x] | [x] |
| Findings ordenados de CRITICAL a LOW | [x] | [x] | [x] |
| Mínimo de 5 findings | [x] 32 | [x] 20 | [x] 51 |
| Detecção de APIs deprecated incluída | [x] nenhuma encontrada | [x] nenhuma encontrada | [x] 2 encontradas |
| Pausa e confirmação antes da Fase 3 | [x] | [x] | [x] |
| **Fase 3** | | | |
| Estrutura de diretórios em MVC | [x] | [x] | [x] |
| Configuração em módulo de config, sem hardcoded | [x] | [x] | [x] |
| Models abstraem os dados | [x] | [x] | [x] |
| Views/Routes separadas | [x] | [x] | [x] |
| Controllers concentram o fluxo | [x] | [x] | [x] |
| Error handling centralizado | [x] | [x] | [x] |
| Entry point claro | [x] | [x] | [x] |
| Aplicação inicia sem erros | [x] | [x] | [x] |
| Endpoints originais respondem | [x] 18 de 19 | [x] 3 de 3 | [x] 22 de 22 |

Observações sobre o checklist:

- **Projeto 1, 18 de 19:** `POST /admin/query` executava qualquer SQL recebido e foi removido de propósito. Passou a responder 404.
- **Projeto 3, um finding em aberto:** a classe `NotificationService` continua sem ser chamada por nenhum endpoint. A skill corrigiu as credenciais, o log e a API deprecated dela, mas não a conectou (a API passaria a enviar e-mail, o que é funcionalidade nova) nem a apagou. Por isso o resumo da skill marca "Zero anti-patterns remaining" como falha, com 50 de 51 resolvidos.
- **Pausa nos projetos 2 e 3:** a skill foi executada de ponta a ponta com a confirmação já dada no pedido. O relatório foi salvo antes de qualquer alteração no projeto.

### Aplicações rodando após a refatoração

Depois de cada execução, a aplicação foi iniciada em uma porta livre, com banco temporário, e os endpoints foram chamados com `curl`. Os resumos completos da skill estão em `report/refactor-summary.md`, dentro da pasta da skill de cada projeto.

**Projeto 1**

```
GET  /                         200    POST   /produtos              201
GET  /health                   200    PUT    /produtos/11           200
GET  /produtos                 200    DELETE /produtos/11           200
GET  /produtos/1               200    POST   /usuarios              201
GET  /produtos/busca?q=mouse   200    POST   /login (senha certa)   200
GET  /usuarios                 200    POST   /login (senha errada)  401
GET  /usuarios/1               200    POST   /login (' OR 1=1 --)   401
GET  /pedidos                  200    POST   /pedidos               201
GET  /pedidos/usuario/1        200    PUT    /pedidos/1/status      200
GET  /relatorios/vendas        200    POST   /admin/reset-db        403 sem token, 200 com token
                                      POST   /admin/query           404 (removido)
```

**Projeto 2**

```
POST   /api/checkout (cartão aprovado)     200  {"msg":"Sucesso","enrollment_id":2}
POST   /api/checkout (cartão recusado)     400  Pagamento recusado
GET    /api/admin/financial-report         200 com x-admin-token, 403 sem
DELETE /api/users/1                        200 com x-admin-token
```

**Projeto 3**

```
GET /                  200    POST   /tasks                       201
GET /health            200    PUT    /tasks/1                     200
GET /tasks             200    DELETE /tasks/2                     200
GET /tasks/1           200    POST   /users                       201
GET /tasks/search      200    PUT    /users/2                     200 com X-Admin-Token, 403 sem
GET /tasks/stats       200    DELETE /users/3                     200 com X-Admin-Token
GET /users             200    POST   /login (senha certa)         200
GET /users/1           200    POST   /login (senha errada)        401
GET /users/1/tasks     200    POST   /categories                  201
GET /reports/summary   200    PUT    /categories/1                200
GET /reports/user/1    200    DELETE /categories/2                200
GET /categories        200
```

No projeto 3, a skill também comparou 70 chamadas antes e depois da refatoração. Os códigos de status são iguais, exceto dois casos que respondiam 500 e passaram a responder 400 (entrada inválida).

### Mudanças de comportamento

Todas vêm de findings de segurança e estão listadas nos resumos da skill. As principais:

- **Senhas:** deixaram de ser devolvidas nas respostas e passaram a ser gravadas com hash com salt, nos três projetos. As senhas dos usuários de exemplo vêm de variáveis `SEED_*`.
- **Endpoints administrativos:** exigem um token no cabeçalho, igual à variável `ADMIN_TOKEN`. Sem a variável definida, respondem 403.
  - Projeto 1: `POST /admin/reset-db`
  - Projeto 2: `GET /api/admin/financial-report` e `DELETE /api/users/:id`
  - Projeto 3: `PUT /users/<id>`, `DELETE /users/<id>` e `POST /users` com `role` diferente de `user`
- **Segredos:** saíram do código e do `/health`. Cada projeto tem um `.env.example` com os nomes das variáveis.
- **Erros:** respostas 500 não trazem mais o texto da exceção, e entradas inválidas que causavam 500 respondem 400.
- **Debug:** desligado por padrão.

### Como a skill se comportou em cada stack

- **Flask sem camadas (projeto 1):** criou a estrutura completa e moveu o código por domínio. Foi o caso mais direto.
- **Express (projeto 2):** os mesmos arquivos de referência funcionaram sem ajuste. A skill converteu os callbacks aninhados em uma conexão com fila e transação, e manteve as respostas em texto puro que a API original usava.
- **Flask com camadas parciais (projeto 3):** não reconstruiu o que existia. Manteve `models/`, `routes/` e `services/` com os mesmos nomes de arquivo, tirou queries e regras das rotas e criou `controllers/`. Foi o projeto com mais findings, a maioria MEDIUM e LOW, e o único com APIs deprecated.
- **Limites observados:** a skill só reporta o que está no catálogo. Ela deixou de fora, por exemplo, dependências sem uso no `requirements.txt` do projeto 3 e o fato de o checkout do projeto 2 não conferir a senha de um e-mail já cadastrado.

---

## D) Como Executar

### Pré-requisitos

- [Claude Code](https://docs.claude.com/en/docs/claude-code/overview) instalado e autenticado
- Python 3.10 ou superior (projetos 1 e 3)
- Node.js 18 ou superior (projeto 2)
- Git

### Executar a skill

A skill está em `.claude/skills/refactor-arch/` dentro de cada projeto. Rode a partir da pasta do projeto:

```bash
# Projeto 1
cd code-smells-project
claude "/refactor-arch"

# Projeto 2
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3
cd ../task-manager-api
claude "/refactor-arch"
```

Em cada execução:

1. A Fase 1 imprime o resumo do projeto.
2. A Fase 2 imprime o relatório, salva em `.claude/skills/refactor-arch/report/audit-report.md` e pergunta `Proceed with refactoring (Phase 3)? [y/n]`.
3. Com **y**, a Fase 3 refatora, valida e salva o resumo em `report/refactor-summary.md`. Com **n**, nada é alterado.

Para salvar o relatório em outro lugar, passe o caminho como argumento:

```bash
claude "/refactor-arch ../reports/audit-project-1.md"
```

Como os projetos deste repositório já estão refatorados, para ver a skill agindo sobre o código original use o commit inicial: `git checkout 6d1ce62 -- code-smells-project/app.py` e os demais arquivos, ou um clone do [repositório base](https://github.com/devfullcycle/mba-ia-refactor-projects-skill) com a pasta `.claude` copiada para dentro do projeto.

### Validar que a refatoração funcionou

**Projeto 1** (porta padrão 5001)

```bash
cd code-smells-project
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
SEED_ADMIN_PASSWORD=admin12345 ADMIN_TOKEN=meu-token python app.py
# em outro terminal
curl -i http://localhost:5001/health
curl -i http://localhost:5001/produtos
```

A porta padrão do projeto original era 5000. Ela ficou em 5001 porque a 5000 é usada pelo AirPlay no macOS. Para usar outra, defina `PORT`.

**Projeto 2** (porta padrão 3000)

```bash
cd ecommerce-api-legacy
npm install
ADMIN_TOKEN=meu-token npm start
# em outro terminal
curl -i -H "x-admin-token: meu-token" http://localhost:3000/api/admin/financial-report
```

As chamadas do `api.http` continuam valendo. As duas rotas administrativas usam o cabeçalho `x-admin-token`.

**Projeto 3** (porta padrão 5000)

```bash
cd task-manager-api
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export SEED_ADMIN_PASSWORD=admin12345 SEED_USER_PASSWORD=user12345 SEED_MANAGER_PASSWORD=manager12345 ADMIN_TOKEN=meu-token
python seed.py
python app.py            # ou: PORT=5050 python app.py
# em outro terminal
curl -i http://localhost:5000/tasks
curl -i http://localhost:5000/reports/summary
```

Em todos os projetos, as variáveis disponíveis estão no `.env.example`.
