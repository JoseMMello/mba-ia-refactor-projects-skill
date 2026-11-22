# MVC Architecture Guidelines

Knowledge for **Phase 3**. This is the target architecture. Apply it with the conventions of the project's own language and framework.

## 1. Layers and responsibilities

| Layer | Owns | Must not |
|---|---|---|
| **Model** | Data structure, queries and persistence, rules that belong to the data itself (totals, valid states, password hashing) | Read the HTTP request, build HTTP responses, know about routes |
| **View / Routes** | Mapping of method and path to a controller function; in an API, the response format (serialization) | Contain business rules or queries |
| **Controller** | The flow of one request: read the input, validate it, call models or services, choose the status code and response | Write SQL or ORM queries, hold configuration |

In a JSON API there are no HTML templates. The View is the routing layer plus the serialization of responses.

Supporting pieces around the three layers:

| Piece | Owns |
|---|---|
| **Config** | Every setting and secret, read from environment variables, in one module |
| **Database** | Creation of the connection or session, in one module |
| **Middlewares** | Cross-cutting concerns: central error handling, authentication, request logging |
| **Services** (optional) | Business flows that involve several models or external systems (payment, notification). Keep an existing services layer. Create one only when a flow does not fit a single model. |
| **Entry point** | The composition root: loads config, creates the app, registers routes and middlewares, starts the server. No business rules. |

## 2. Dependency direction

```
entry point -> routes -> controllers -> services (optional) -> models -> database
                                  config is read by any layer
```

- A layer only calls the layer to its right.
- Models never import controllers or routes.
- Routes never import the database module.
- No circular imports.

## 3. Target structure

Adapt the names to the stack and to what the project already uses. Keep one file per domain entity in each layer.

Python (Flask or similar):

```
<project>/
├── app.py                  # entry point, composition root
├── config/settings.py
├── database.py             # connection or session
├── models/<entity>_model.py
├── controllers/<entity>_controller.py
├── routes/<entity>_routes.py      # blueprints
├── middlewares/error_handler.py
├── services/               # only when needed or already present
├── requirements.txt
└── .env.example
```

Node.js (Express or similar):

```
<project>/
├── package.json
├── .env.example
└── src/
    ├── app.js              # entry point, composition root
    ├── config/index.js
    ├── database/connection.js
    ├── models/<entity>Model.js
    ├── controllers/<entity>Controller.js
    ├── routes/<entity>Routes.js
    ├── middlewares/errorHandler.js
    └── services/           # only when needed or already present
```

For other stacks, use the same layers with the idiomatic folder and file names of that stack.

## 4. Rules

1. **Configuration**: no secret, credential, port or database path as a literal in the code. One config module reads them from the environment. Development defaults are allowed only for values that are not secret. Provide `.env.example` with the variable names and no real values.
2. **Debug off by default**: debug mode comes from configuration and defaults to off.
3. **Thin routes**: a route file only maps a path to a controller function.
4. **Controllers do not query**: all data access goes through a model.
5. **Models do not know HTTP**: no request or response objects inside models.
6. **Central error handling**: one handler turns errors into a consistent JSON response. Controllers raise or forward errors instead of repeating `try/except` or `try/catch`. Internal details never go to the client.
7. **Validation before use**: input is validated in the controller, or in a validator it calls, before reaching the model.
8. **Sensitive fields never leave**: passwords, hashes, tokens and secrets are not serialized in responses.
9. **Safe queries**: placeholders for every value.
10. **One connection module**: no connection created in a route or controller.
11. **Naming**: follow the conventions of the language (`snake_case` in Python, `camelCase` in JavaScript) and the naming already used by the project's domain. Do not translate entity names.

## 5. Adapting to the starting point

| Starting point | What to do |
|---|---|
| No layers (everything in a few files) | Create the full structure and move the code, one domain at a time |
| Partial layers (folders exist but leak) | Keep the existing folders and names. Move only what is in the wrong layer. Add the missing pieces: controllers, config, error handler. Do not rebuild what is already correct. |
| Already layered | Fix the findings in place. No structural change is needed beyond what a finding requires. |

Always:

- Keep every original endpoint with the same method, path, and request and response format.
- Keep the original start command working, or state the new one.
- Keep the database schema and the existing data.
- Prefer several small moves, checking that the application still boots, over one large rewrite.
- Delete the old files once their code has moved, so nothing is duplicated.

## 6. Checklist for the result

- [ ] Directory structure follows MVC
- [ ] Configuration extracted to a config module, nothing hardcoded
- [ ] Models abstract the data
- [ ] Views / routes separated
- [ ] Controllers hold the request flow
- [ ] Error handling centralized
- [ ] Clear entry point
- [ ] Application boots without errors
- [ ] Original endpoints respond correctly
