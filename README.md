# Product Management REST API with Test-Driven and Behavior-Driven Development

IBM TDD/BDD assignment implementation in Python. Includes a persistent SQLAlchemy product model, Flask REST API, browser UI, factory-generated test products, model/API tests, and seven Behave/Selenium scenarios.

## Run

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m flask --app service run
```

Open http://127.0.0.1:5000. SQLite is the default database; set `DATABASE_URI` to change it.

## Tests

```bash
python -m coverage run --source=service -m pytest -q
python -m coverage report -m
python -m behave --dry-run --format progress
python -m behave --format progress
```

Unit tests use an isolated in-memory database. BDD starts its own local HTTP server and in-memory database. Chrome and ChromeDriver are required for browser execution. Selenium Manager can locate/download them; alternatively set `CHROME_BINARY` and `CHROMEDRIVER`.

## Verified results

- Model/API suite: **21 passed, 10 subtests passed**.
- Service statement coverage: **100% (136/136 statements)**.
- Behave dry run: **7 scenarios, 97 steps resolved; no undefined steps**. A dry run does not execute scenario assertions.
- Full browser execution: **blocked before scenarios ran**. Chrome exited because the execution environment denied its process-singleton socket (`Operation not permitted`). No BDD scenarios are claimed to have passed.

## Submission and feedback

See [SUBMISSION.md](SUBMISSION.md) for all 31 task URLs with line anchors.

The supplied prior feedback awarded 26/34 points. Question 5 and questions 21–27 lost points. The LIST ALL test now verifies an empty database, persists two products, and checks their identities and contents. BDD uses `press`, checks success messages and original descriptions, validates the `Hat` / `A red fedora` fields, and tests filter inclusion/exclusion. The background is shared across scenarios. Dropdown checks use visible labels rather than input-field assertions.

All 31 requested code locations are present. The supplied feedback for several failed scenarios was nonspecific; this implementation addresses the stated issues, but a future grading score is not verified or guaranteed.
