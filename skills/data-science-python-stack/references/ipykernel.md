# ipykernel

The Python kernel for Jupyter — the bridge that lets notebook clients
(JupyterLab, VS Code, IDE plugins) execute Python code.

**Use ipykernel for:**
- Interactive programming inside an IDE (VS Code, Cursor, PyCharm,
  JupyterLab, …). The IDE talks to ipykernel to run cells, inspect
  variables, and keep state alive between executions.
- Registering an environment as a named kernel so it appears in the
  IDE / JupyterLab kernel picker (one kernel per project / virtualenv).
- An agent (including this one) can drive a running kernel the same way
  an IDE does — execute code, read outputs, keep state across turns —
  whenever a persistent Python session is more useful than one-shot
  `python -c` calls.

**You almost never call ipykernel directly.** Install it inside the
project's environment so the IDE can launch a kernel against that
environment, or register a named kernel with
`python -m ipykernel install --user --name <env-name>`.
