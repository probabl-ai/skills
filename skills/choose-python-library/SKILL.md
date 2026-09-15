---
name: choose-python-library
description: >
  Resolve a genuine choice between Python libraries for one job,
  then ask the environment manager to add the chosen dependency.
  Trigger for competing-library questions or an optional package not
  already fixed by the project stack.
---

# Choose Python Library

1. State the job and constraints.
2. Check `data-science-python-stack`; if it already assigns one
   canonical library to the job, use it rather than reopening the
   choice.
3. For a genuine choice, present the smallest useful option set and
   ask the user. Do not pick silently.
4. After the user chooses, dispatch `python-env-manager` and use
   `python -m skore_skills env add <package>`.
5. Confirm symbols with `python -m skore_skills api get <dotted>`
   before writing calls.

## Stop conditions

- Do not install every candidate.
- Do not use popularity alone as a technical decision.
- Do not run pip directly in a managed project.
- Do not substitute black/isort for Ruff or sklearn Pipeline for
  skrub DataOps; those choices are already fixed.

This action is intentionally small pending review of decision
criteria.
