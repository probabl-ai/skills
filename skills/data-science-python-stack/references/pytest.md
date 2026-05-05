# pytest

The standard Python testing framework. The default for everything from
unit tests to integration tests in modern Python projects.

**Pick pytest when:**
- Any time you write tests in this stack. There is no real alternative
  worth picking.

**Notes for orchestration:**
- For data-science code, write tests against small synthetic fixtures,
  not real datasets. Real-data validation belongs in a separate script
  or notebook, not in the test suite.
- Long-running ML training is a poor fit for unit tests — keep training
  out of the suite and test the surrounding logic (data loading,
  preprocessing, metrics, persistence) instead.
