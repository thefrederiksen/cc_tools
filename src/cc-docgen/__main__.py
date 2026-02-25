"""Entry point for running cc_docgen as a module.

Usage: python -m cc_docgen generate
"""

from cc_docgen.cli import cli

if __name__ == "__main__":
    cli()
