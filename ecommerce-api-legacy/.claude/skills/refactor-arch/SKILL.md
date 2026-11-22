---
name: refactor-arch
argument-hint: "[path to save the audit report]"
description: Audits a backend codebase for architecture, security and code quality problems, then refactors it to the MVC pattern and validates that it still works. Works with any language or framework. Use when asked to audit, review or refactor the architecture of a project.
---

# Refactor Architecture

You audit the project in the current directory and refactor it to MVC. The work has three phases. Run them in order, finish each one before starting the next, and never skip one.

The knowledge for each phase is in the `references/` folder next to this file. Read the file named in each phase before doing that phase.

## Phase 1: Analysis

1. Read `references/project-analysis.md`.
2. Follow its heuristics to detect the language, framework, dependencies, database, domain, entry point, endpoints and current architecture.
3. Read every source file in full. Phase 2 needs exact line numbers.
4. Print the Phase 1 summary block exactly as that file defines it.

Do not change any file in this phase.

## Phase 2: Audit

1. Read `references/anti-patterns.md` and `references/report-template.md`.
2. Check every source file against every entry in the catalog, using the detection signals. Include the check for deprecated APIs.
3. For each finding, record the severity, the file, the exact line or line range, a description, the impact and the recommendation. Open the file again to confirm the line numbers before writing them.
4. Report only what is in the code. Never invent a finding to reach a number, and never report a pattern that the project does not have.
5. Print the report in the format of `references/report-template.md`, with the findings ordered from CRITICAL to LOW.
6. Report file: `$ARGUMENTS`
   Save the report, exactly as printed and with nothing else in the file. This is the only file that may be written before the confirmation.
   - If the line above has a file path, save to that path.
   - If it has no path, save to `report/audit-report.md` inside this skill's folder, next to `references/`, creating the `report/` folder if needed. Overwrite the file if it already exists.
   - Print the path of the saved file.
7. Then stop and ask exactly this:

   `Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]`

**Do not create, edit, move or delete any project file until the user answers yes.** If the answer is no, or anything other than a clear yes, end here and leave the project untouched.

## Phase 3: Refactoring

Start only after the user confirmed.

1. Read `references/mvc-guidelines.md` and `references/refactoring-playbook.md`.
2. Plan the target structure for this project and its stack, following the guidelines. Adapt to what exists: a project with no layers gets the full structure, and a project that already has layers keeps what is correct and has only its problems fixed.
3. Fix every finding from Phase 2 with the matching transformation from the playbook, starting with CRITICAL and ending with LOW.
4. Keep the public behavior: every endpoint listed in Phase 1 keeps its method, path, and request and response format. If fixing a security finding requires changing a response (for example, no longer returning passwords), say so in the final summary.
5. Keep the project runnable the same way: update the entry point, imports and dependency manifest so the original start command still works, or state the new command.
6. Validate:
   - Start the application and confirm that it boots without errors. If the default port is busy on this machine, start it on a free port through configuration for the validation. Do not change the project's default port because of that.
   - Call every endpoint from the Phase 1 inventory and confirm that it responds. Use a test or temporary database when a call would destroy data.
   - Search the code again for the anti-patterns that were reported and confirm that they are gone.
   - Stop the application when the validation ends.
7. If something fails, fix it and validate again. Do not print the final summary while the application does not boot or an original endpoint does not respond.
8. Print the Phase 3 summary below. Then save it, exactly as printed and with nothing else in the file, as `refactor-summary.md` in the same folder where the audit report was saved, overwriting the file if it exists, and print the path of the saved file.

```
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
<directory tree of the refactored project>

Removed: <old files whose code was moved, or "none">

## Findings Resolved
<n> of <n> (list any finding left open or only partly resolved, with the reason)

## Validation
  <ok or fail> Application boots without errors
  <ok or fail> All endpoints respond correctly (<n> of <n>)
  <ok or fail> Zero anti-patterns remaining

## Behavior Changes
<intentional changes to responses, or "none">
================================
```

## Rules for all phases

- Detect, do not assume. Everything printed comes from the files of this project.
- If a reference file named in a phase does not exist, stop and report which file is missing. Do not continue from general knowledge.
- Use paths relative to the project root.
- Stay inside the project directory. Do not touch files outside it, except the audit report file when the user gave a path outside it.
- Never change `SKILL.md` or the files in `references/`. They are read-only. The audit report and the refactor summary are the only files written inside the skill's folder.
- Do not add features, endpoints or dependencies that the refactor does not need.
- Keep secrets out of the code and out of the output. Move them to configuration read from the environment, with a `.env.example` listing the variable names.
