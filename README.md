# ksau-py

A Python implementation of ksau focused on ease-of-use, with a trade-off in
performance compared to [ksau-go](https://github.com/global-index-source/ksau-go).

## Development

### Prerequisites

- `uv` package manager
- `ruff` (included in dev dependencies)

### Getting Started

Install dependencies:

```bash
uv sync
```

### Code Quality

Before committing, ensure code quality by running:

```bash
uvx ruff check --fix && uvx ruff format
```

> Note: Please fix any remaining linting errors manually
> and minimize the use of `# noqa` directives.
