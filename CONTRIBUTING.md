# Contributing

## Development setup
1. Create a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```
3. Run tests:
   ```bash
   pytest -q
   ```

## Pull requests
- Keep changes focused and small.
- Add or update tests when behavior changes.
- Update documentation/examples when relevant.
- Ensure `pytest -q` passes before opening the PR.
