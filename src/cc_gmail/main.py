#!/usr/bin/env python3
"""Entry point for cc_gmail CLI."""

import sys
from pathlib import Path

# Add src to path for PyInstaller compatibility
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    base_path = Path(sys._MEIPASS)
else:
    # Running as script
    base_path = Path(__file__).parent

sys.path.insert(0, str(base_path))

from src.cli import app

if __name__ == "__main__":
    app()
