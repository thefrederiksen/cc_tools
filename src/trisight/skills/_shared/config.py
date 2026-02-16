"""Configuration loading for TriSight skills.

Resolution order for cc_click path:
  1. CC_CLICK_PATH environment variable
  2. Default path in cc_tools
"""
import os

# Updated default paths
_DEFAULT_CC_CLICK = (
    r"D:\ReposFred\cc_tools\src\cc_click\src\CcClick\bin\Release\net10.0-windows\CcClick.exe"
)

_DEFAULT_TRISIGHT_CLI = (
    r"D:\ReposFred\cc_tools\src\trisight\TrisightCli\bin\Release\net10.0-windows10.0.17763.0\TrisightCli.exe"
)


def get_cc_click_path() -> str:
    """Resolve cc_click.exe path."""
    env = os.environ.get("CC_CLICK_PATH")
    if env:
        return env
    return _DEFAULT_CC_CLICK


def get_trisight_cli_path() -> str:
    """Resolve TrisightCli.exe path."""
    env = os.environ.get("CC_TRISIGHT_CLI_PATH")
    if env:
        return env
    return _DEFAULT_TRISIGHT_CLI


def get_python_path() -> str:
    """Resolve Python interpreter path."""
    env = os.environ.get("CC_PYTHON_PATH")
    if env:
        return env
    return "python"
