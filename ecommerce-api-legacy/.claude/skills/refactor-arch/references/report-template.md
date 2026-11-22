# Audit Report Template

Format for the **Phase 2** output. Print the report exactly in this structure. Replace everything between `<` and `>`.

## Template

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <project folder name>
Stack:   <language> + <framework>
Files:   <n> analyzed | ~<n> lines of code

## Summary
CRITICAL: <n> | HIGH: <n> | MEDIUM: <n> | LOW: <n>
Deprecated APIs: <number of distinct deprecated APIs found, with their names, or "none found">

## Findings

### [<SEVERITY>] <Anti-pattern name> (<catalog id>)
File: <relative/path.ext>:<line or line range, several allowed>
Description: <what the code does, with the concrete detail found>
Impact: <what can go wrong because of it>
Recommendation: <what to change, naming the playbook transformation>

### [<SEVERITY>] <next finding>
...

================================
Total: <n> findings
================================
```

## Rules

1. Order the findings by severity: all CRITICAL first, then HIGH, MEDIUM, LOW. Inside a severity, order by file path.
2. Every finding has the five fields: title line, File, Description, Impact, Recommendation.
3. `File:` always has a path relative to the project root and exact line numbers, such as `models.py:28` or `src/app.js:40-72`. Several locations are separated by commas.
4. `Description` states the fact found in this project, not the generic definition. Quote the name or value involved, but never print a full secret: show only the variable name and where it is.
5. The numbers in `Summary` and `Total` must match the findings listed. Count them before printing.
6. Use the anti-pattern names and ids from `anti-patterns.md`.
7. No finding without evidence. If the project has fewer problems, the report is shorter.
8. Write the report in English, keeping identifiers from the code as they are.

## Example of one finding

```
### [CRITICAL] SQL Injection (AP-01)
File: models.py:28, 47-50, 109-111
Description: Queries are built by concatenating request values into the SQL string, including the login query that receives e-mail and password.
Impact: An attacker can read or delete any table and log in without a password.
Recommendation: Use parameterized queries (T-01) in every data access function.
```

## After the report

Print this line and wait for the answer:

```
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```
