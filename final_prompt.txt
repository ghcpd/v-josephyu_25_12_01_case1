# Task: Documentation & Knowledge Sub-Types Verification for Flask Logging System

You are provided with a Flask-based logging management system using SQLite (`data.db` expected in the application directory, same folder as `app.py`).
Use `.venv` as environment.
Follow `README.md` to test all code examples.
Verify that documentation (missing, outdated, incorrect, tutorials, onboarding) is consistent with the actual implementation.
Identify all mismatches between documentation and actual implementation.
Generate `corrected_readme.md` with working examples.
Print all discovered defects to `defects.txt` with error traces and classification by sub-type.

## Sub-Types to Cover

- Missing docs: features or APIs used in code but not documented.
- Outdated docs: behaviors changed in code but docs still reflect old behavior.
- Incorrect docs: wrong parameters, values, or paths.
- Tutorials: example commands that do not run as described.
- Onboarding: unclear or broken setup steps.

## Expected Output

1. `defects.txt` - List of all defects found (categorized by sub-type) with error messages or exact mismatches.
2. `corrected_readme.md` - Fixed version of the tutorial with working instructions and examples.
3. `requirements.txt` - Add required libraries based on the `.venv` environment.
4. `setup.ps1` and `setup.sh` - PowerShell and bash scripts to set up the environment on Windows and Linux.
5. `test_files` - Minimal test files to verify critical endpoints and DB usage.
6. `run_tests.ps1` and `run_tests.sh` - PowerShell and bash scripts to run the tests on Windows and Linux.

## Notes

- Use Windows PowerShell 5.1 compatible commands.
- Verify the DB file location constraint: must be `data.db` in the application directory.
- Ensure API examples accept and validate `context` as JSON object.
- Confirm allowed `level` values match documentation.
- Ensure all test should use pytest.