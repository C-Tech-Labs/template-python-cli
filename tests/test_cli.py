import json
import os
import subprocess
import sys

CLI_MODULE = [sys.executable, "-m", "template_python_cli.cli"]


def run_cli(args, env=None):
    result = subprocess.run(CLI_MODULE + args, capture_output=True, env=env)
    return result.returncode, result.stdout.decode(), result.stderr.decode()


def test_cli_help():
    code, stdout, _ = run_cli(["--help"])
    assert code == 0
    assert "Template Python CLI" in stdout


def test_cli_default_output():
    code, stdout, _ = run_cli([])
    assert code == 0
    assert stdout.strip() == "Hello, world!"


def test_cli_config_file(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps({"name": "Ada", "greeting": "Welcome", "repeat": 2}), encoding="utf-8")

    code, stdout, _ = run_cli(["--config", str(config_path)])
    assert code == 0
    lines = [line.strip() for line in stdout.splitlines() if line.strip()]
    assert lines == ["Welcome, Ada!", "Welcome, Ada!"]


def test_cli_environment_override(monkeypatch):
    env = os.environ.copy()
    env.update({
        "TEMPLATECLI_NAME": "Ops",
        "TEMPLATECLI_GREETING": "Welcome",
        "TEMPLATECLI_REPEAT": "1",
    })
    code, stdout, _ = run_cli([], env=env)
    assert code == 0
    assert stdout.strip() == "Welcome, Ops!"


def test_cli_json_output():
    code, stdout, _ = run_cli(["--name", "API", "--output-format", "json"])
    assert code == 0
    payload = json.loads(stdout)
    assert payload["messages"] == ["Hello, API!"]


def test_cli_dry_run():
    code, stdout, _ = run_cli(["--name", "Dry", "--dry-run"])
    assert code == 0
    payload = json.loads(stdout)
    assert payload["name"] == "Dry"
    assert payload["greeting"] == "Hello"


def test_cli_invalid_repeat():
    code, _, stderr = run_cli(["--repeat", "0"])
    assert code == 1
    assert "repeat must be at least 1" in stderr
