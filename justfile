set shell := ["bash", "-e", "-o", "pipefail", "-c"]
set dotenv-path := "./.env"
set dotenv-load

test *args:
    @uv run pytest {{args}}

cov *args:
    @uv run pytest --cov=src {{args}}

check:
    @uvx ruff check --fix .
    @uvx ruff format .
    @uvx pyright .

ci-lint:
    @uvx ruff check .
    @uvx ruff format --check .
    @uvx pyright .
