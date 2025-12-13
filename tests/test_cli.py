import subprocess
import sys


def test_cli_help():
    result = subprocess.run([sys.executable, "-m", "template_python_cli.cli", "--help"], capture_output=True)
    assert result.returncode == 0
    assert b"Usage" in result.stdout
