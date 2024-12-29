# AI Reader 9000 (frontend)
This is the repo for the frontend code for AI Reader 9000, a RAG chatbot which answers any question with direct quotes from the source material.

The frontend uses streamlit and is available online at aireader9000.streamlit.app

# Development Guidelines
## Setting up Dev Environment
This project uses `uv` for python project management, including the virtual environment (at .venv).

To crete the virtual environment, activate it, and install project dependencies from the `pyproject.toml` and `uv.lock` files in this repo, run the following commands:
```bash
uv venv --python 3.13.1   
source .venv/bin/activate
uv sync
uv run pre-commit install # one last 'manual' cmd still needed to install .git hooks
```

If you want to add a required library to the project, you can add it manually to the dependencies in `pyproject.toml` and then run `uv sync` to install it, or alternatively you can run `uv add <package-name>` from your shell (which will install it and update the `prpoject.toml` file).

## Deploying the streamlit app Locally
To run the streamlit app locally, run the following command:
```bash
PYTHONPATH=. streamlit run home.py
```

## Updating the Deployed Streamlit App Online
The app online at aireader9000.streamlit.app is deployed from the `main` branch of this repo, so any (successful) updates to the main branch of this repo will be deployed to the online app.

## Code Quality, CI/CD 
This project uses `ruff` and `mypy` to maintain code quality, for linting and type checking, respectively. We run these checks via CI/CD on push to main, but also locally via `pre-commit` hooks. The `pre-commit` hooks are configured in the `.pre-commit-config.yaml` checked into this repository.
