"""Command-line entry point for the template CLI."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Iterable, List

from template_python_cli import __version__
from template_python_cli.config import (
    DEFAULT_ENV_PREFIX,
    AppConfig,
    build_config,
    load_config_file,
    load_environment,
)

LOG = logging.getLogger("template_python_cli")


def configure_logging(verbosity: int, quiet: bool) -> None:
    """Configure global logging level based on verbosity flags."""

    if quiet:
        level = logging.ERROR
    else:
        level = logging.WARNING
        if verbosity == 1:
            level = logging.INFO
        elif verbosity >= 2:
            level = logging.DEBUG
    logging.basicConfig(level=level, format="%(levelname)s:%(name)s:%(message)s")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Template Python CLI with batteries included")
    parser.add_argument("--name", help="Name to greet")
    parser.add_argument("--greeting", default=None, help="Greeting to use (default: Hello)")
    parser.add_argument("--punctuation", default=None, help="Sentence punctuation (default: !)")
    parser.add_argument("--repeat", type=int, default=None, help="Number of times to repeat the message")
    parser.add_argument("--loud", action="store_true", help="Shout the message in uppercase")
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Path to a YAML or JSON config file containing defaults",
    )
    parser.add_argument(
        "--env-prefix",
        default=DEFAULT_ENV_PREFIX,
        help=f"Environment variable prefix (default: {DEFAULT_ENV_PREFIX})",
    )
    parser.add_argument(
        "--output-format",
        choices=["text", "json"],
        default="text",
        help="Render greetings as plain text or JSON",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print resolved configuration without running")
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity (use -vv for debug)",
    )
    parser.add_argument("-q", "--quiet", action="store_true", help="Silence informational logs")
    parser.add_argument("--version", action="version", version=f"template-python-cli {__version__}")
    return parser


def generate_messages(config: AppConfig) -> List[str]:
    """Create one or more greeting messages from configuration."""

    template = f"{config.greeting}, {config.name}{config.punctuation}"
    if config.loud:
        template = template.upper()
    return [template for _ in range(config.repeat)]


def render_output(messages: Iterable[str], output_format: str) -> str:
    if output_format == "json":
        return json.dumps({"messages": list(messages)}, indent=2)
    return "\n".join(messages)


def resolve_configuration(args: argparse.Namespace) -> AppConfig:
    file_config = load_config_file(args.config)
    env_config = load_environment(args.env_prefix)
    cli_config = {
        "name": args.name,
        "greeting": args.greeting,
        "punctuation": args.punctuation,
        "repeat": args.repeat,
        "loud": args.loud,
    }
    return build_config(file_config, env_config, cli_config)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    configure_logging(args.verbose, args.quiet)

    try:
        config = resolve_configuration(args)
    except Exception as exc:  # noqa: BLE001
        LOG.error("Configuration error: %s", exc)
        return 1

    if args.dry_run:
        print(json.dumps(config.to_dict(), indent=2))
        return 0

    LOG.debug("Resolved configuration: %s", config)
    messages = generate_messages(config)
    output = render_output(messages, args.output_format)
    print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
