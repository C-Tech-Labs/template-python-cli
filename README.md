# template-python-cli

A production-ready template for building Python command-line applications with confidence. The project is opinionated toward reliable operations: layered configuration (flags, config files, environment variables), structured logging, type-checked configuration parsing, and fully documented workflows so you can focus on shipping features rather than wiring up boilerplate.

---

## What you get
- **Modern packaging** via `pyproject.toml` with an installable console script (`template-python-cli`). Optional extras (e.g., `yaml`) keep optional dependencies out of your base install.
- **Layered configuration**: YAML/JSON config files, environment variables (prefix `TEMPLATECLI_`), and CLI flags with sensible defaults and validation.
- **Rich CLI ergonomics**: verbosity controls, dry-run mode, JSON or plaintext output, version reporting, and consistent exit codes.
- **Typed configuration** using `dataclasses` with guardrails for invalid values (e.g., non-positive repeat counts).
- **Developer productivity**: pytest suite, Ruff linting configuration, architecture docs, changelog, and ready-to-run config examples.

## Quickstart
1. Create a virtual environment and install the project in editable mode with development tooling:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   pip install -e .[dev]
   ```

2. Inspect the available options and built-in documentation:
   ```bash
   template-python-cli --help
   template-python-cli --version
   ```

3. Run the CLI with defaults:
   ```bash
   template-python-cli
   # Hello, world!
   ```

4. Experiment with the examples:
   ```bash
   template-python-cli --config examples/config.json
   template-python-cli --config examples/config.yaml --output-format json
   ```

## Usage examples
### Basic greeting
```bash
template-python-cli --name "Cardale" --greeting "Welcome"
```

### Repeat and shout
```bash
template-python-cli --name "Team" --repeat 3 --loud
# WELCOME, TEAM!
# WELCOME, TEAM!
# WELCOME, TEAM!
```

### JSON output for automation
```bash
template-python-cli --name "API" --output-format json
# {
#   "messages": [
#     "Hello, API!"
#   ]
# }
```

### Dry-run for configuration inspection
```bash
template-python-cli --config examples/config.json --dry-run
# Prints the resolved configuration without executing the greeting logic
```

### Logging and verbosity controls
```bash
template-python-cli --verbose          # INFO-level logs
template-python-cli --very-verbose     # DEBUG-level logs
template-python-cli --quiet            # Suppress stdout, only errors
```

### Environment-driven execution (12-factor friendly)
```bash
export TEMPLATECLI_NAME="Ops"
export TEMPLATECLI_GREETING="Welcome"
export TEMPLATECLI_REPEAT=2
template-python-cli --output-format json
```

## Configuration reference
Configuration is layered in the following precedence order (lowest to highest):
1. Built-in defaults defined in `AppConfig`.
2. Config file (`--config examples/config.json`). JSON works out-of-the-box; YAML is supported when the optional `yaml` extra is installed (`pip install .[yaml]`).
3. Environment variables using the prefix `TEMPLATECLI_` (customizable via `--env-prefix`).
4. CLI flags.

Supported configuration keys:
- `name` (str): Recipient of the greeting.
- `greeting` (str): Leading text of the message.
- `punctuation` (str): Ending punctuation, default `!`.
- `repeat` (int): Number of times to repeat the message (must be >= 1).
- `loud` (bool): Uppercase the output.
- `metadata` (dict): Optional structured data passed through unchanged (emitted in JSON output).

### Example JSON config
```json
{
  "name": "Automation",
  "greeting": "Howdy",
  "repeat": 2,
  "metadata": {"component": "template-cli", "owner": "platform"}
}
```

### Example YAML config
```yaml
name: Automation
greeting: Hello
repeat: 1
metadata:
  component: template-cli
  owner: platform
```

## Development
- Run tests: `pytest`
- Lint with Ruff: `ruff check .`
- Type-check (optional): `pyright` or `mypy` if you prefer
- Local CLI run without installation: `python -m template_python_cli.cli --help`

### Releasing
1. Update `CHANGELOG.md` and bump the version in `pyproject.toml`.
2. Run the test suite and linters.
3. Build artifacts: `python -m build`.
4. Publish to your index of choice (e.g., `python -m twine upload dist/*`).

## Project structure
- `src/template_python_cli/cli.py`: CLI entry point, argument parsing, runtime orchestration, output formatting.
- `src/template_python_cli/config.py`: Configuration dataclass and loaders for files/env/CLI overrides.
- `examples/config.yaml` / `examples/config.json`: Example configuration files.
- `tests/`: Pytest suite covering CLI behaviors and configuration layering.
- `docs/`: Architecture notes and rationale for design decisions.

## Security notes
No secrets are stored in this template. Use environment variables or a secret manager for sensitive information in downstream applications. The CLI intentionally avoids writing secret values to logs; avoid echoing secrets via `--metadata` or environment variables unless necessary.
