# Project Analysis Heuristics

Knowledge for **Phase 1**. Use it to detect the stack and map the current architecture of any backend project, whatever the language. Phase 1 only reads files. It never changes them.

## 1. What to read, in order

1. The directory tree, ignoring dependency and build folders (`node_modules`, `.venv`, `venv`, `__pycache__`, `dist`, `build`, `.git`).
2. The dependency manifest (section 2).
3. The entry point (section 5).
4. Every source file. The audit in Phase 2 needs exact line numbers, so read the files in full instead of sampling them.
5. `README`, `.env.example`, `*.http` files, Docker and CI files, when they exist.

Always report paths relative to the project root.

## 2. Language detection

| Signal | Language |
|---|---|
| `requirements.txt`, `pyproject.toml`, `Pipfile`, `setup.py`, `*.py` | Python |
| `package.json`, `*.js`, `*.mjs`, `*.cjs` | JavaScript (Node.js) |
| `package.json` with `typescript`, `tsconfig.json`, `*.ts` | TypeScript (Node.js) |
| `pom.xml`, `build.gradle`, `*.java` | Java |
| `go.mod`, `*.go` | Go |
| `composer.json`, `*.php` | PHP |
| `Gemfile`, `*.rb` | Ruby |
| `*.csproj`, `*.cs` | C# |

If more than one language is present, report the one that owns the entry point as the main language and list the others.

## 3. Framework detection

Read the framework and its version from the dependency manifest. Confirm it in the code with the import or bootstrap call.

| Dependency | Confirmation in code | Framework |
|---|---|---|
| `flask` | `from flask import Flask`, `Flask(__name__)` | Flask |
| `django` | `manage.py`, `settings.py` | Django |
| `fastapi` | `FastAPI()` | FastAPI |
| `express` | `require('express')`, `express()` | Express |
| `@nestjs/core` | `@Module`, `NestFactory` | NestJS |
| `fastify` | `fastify()` | Fastify |
| `spring-boot-starter-web` | `@SpringBootApplication` | Spring Boot |
| `gin-gonic/gin` | `gin.Default()` | Gin |
| `laravel/framework` | `artisan` | Laravel |
| `rails` | `config/routes.rb` | Rails |

If the manifest pins a version (`flask==3.1.1`, `"express": "^4.18.2"`), report it. If there is no version, report the name only. Never guess a version.

List the other relevant dependencies too (CORS, ORM, auth, validation, mail, payment libraries).

## 4. Database detection

| Signal | Conclusion |
|---|---|
| `import sqlite3`, `sqlite3` package, `*.db` or `*.sqlite` files | SQLite, raw driver |
| `psycopg2`, `pg`, `postgres://` URLs | PostgreSQL |
| `mysql-connector`, `pymysql`, `mysql2`, `mysql://` URLs | MySQL |
| `pymongo`, `mongoose`, `mongodb://` URLs | MongoDB |
| `flask_sqlalchemy`, `sqlalchemy`, `sequelize`, `prisma`, `typeorm` | ORM in use; name the ORM and the engine behind it |
| Arrays or objects kept in module variables as the only storage | In-memory storage, no database |

To list the tables or collections, look for, in this order: `CREATE TABLE` statements, ORM model classes (`db.Model`, `Model.init`, `@Entity`), migration files, and table names inside queries.

## 5. Entry point and how to run

| Signal | Entry point |
|---|---|
| `if __name__ == "__main__":` with `app.run(...)` | That Python file |
| `"main"` or `scripts.start` in `package.json` | The file named there |
| `app.listen(...)` | The file that calls it |
| `manage.py`, `main.go`, `Program.cs`, `Application.java` | The standard entry of that stack |

Write down the start command, the port and any seed or setup step (`seed.py`, `npm run seed`, migrations). Phase 3 needs them to validate the refactor.

## 6. Endpoint inventory

List every route with method and path. Phase 3 uses this list to confirm that nothing stopped responding. Search for all registration styles of the stack, not only the most common one:

- Python: `@app.route`, `@blueprint.route`, `app.add_url_rule`, `@app.get/post/put/delete`, `@router.get`
- Node.js: `app.get/post/put/patch/delete`, `router.get/...`, `app.use('/prefix', router)`
- Others: route annotations (`@GetMapping`), route files (`routes.rb`, `routes/web.php`)

Remember to add prefixes from blueprints, routers and `app.use` to the final path.

A project can mix styles in the same file. The endpoint total is the sum of the routes found in every style, counted one by one.

## 7. Mapping the current architecture

Find out where each responsibility lives today:

| Responsibility | Look for |
|---|---|
| Routing | Route registration calls |
| Request handling | Reading the request body, query or params; building the HTTP response |
| Business rules | Calculations, validations, status transitions, discounts, permissions |
| Data access | SQL strings, ORM queries, driver calls |
| Configuration | Secrets, ports, database paths, debug flags, credentials |
| Cross-cutting | Error handling, logging, auth, e-mail and notification code |

Then classify the project:

| What you find | Classification |
|---|---|
| Routing, business rules and data access in the same file or function | Monolithic, no layer separation |
| Separate files, but the layers leak (SQL in route handlers, HTTP objects in models, business rules in routes) | Partially layered |
| Folders such as `models/`, `routes/`, `controllers/`, `services/`, each keeping to its role | Layered (MVC or similar) |

A project with layer folders is not automatically well structured. Check what each file really does. For example, a `routes/` file that runs queries and applies business rules is still a route and a controller and a model in one place.

Record the facts that Phase 3 will depend on: global state shared between modules, circular imports, where the database connection is created, and code that runs at import time.

## 8. Domain detection

Infer what the application is for from table names, model names, route paths and the README. Describe it in one line with its main entities, for example `E-commerce API (products, orders, users)` or `Task manager API (tasks, users, categories)`. Use the entity names found in the code.

## 9. Counting

- **Source files**: files in the project's own language(s), excluding dependency folders, build output, caches, lock files and generated files.
- **Lines of code**: approximate total lines of those files.

The count must match what is on disk. Count again before printing.

## 10. Phase 1 output

Print exactly this block, filled with what was detected, and nothing else:

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <language>
Framework:     <framework and version>
Dependencies:  <other relevant dependencies>
Domain:        <one line, with the main entities>
Architecture:  <classification and one line of evidence>
Source files:  <n> files analyzed (~<n> lines)
DB tables:     <tables or collections, or "none detected">
Entry point:   <file and start command>
Endpoints:     <n> routes
================================
```

## 11. When something is unclear

- If a signal is missing, write `not detected` in that field. Do not invent a value.
- If two frameworks or two databases are present, list both and say which one the entry point uses.
- If no source code is found in the current directory, stop and ask for the project path.
