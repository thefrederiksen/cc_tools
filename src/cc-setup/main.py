"""
cc_tools-setup - Windows installer for cc_tools suite
Downloads and installs all cc_tools executables, adds to PATH, installs SKILL.md
"""

import sys
from installer import CCToolsInstaller


def main():
    """Main entry point for the installer."""
    print("=" * 60)
    print("  cc_tools Setup")
    print("  https://github.com/CenterConsulting/cc_tools")
    print("=" * 60)
    print()

    installer = CCToolsInstaller()

    try:
        success = installer.install()
        if success:
            print()
            print("=" * 60)
            print("  Installation complete!")
            print("  Restart your terminal to use cc_tools.")
            print("=" * 60)
            return 0
        else:
            print()
            print("Installation failed. See errors above.")
            return 1
    except KeyboardInterrupt:
        print()
        print("Installation cancelled by user.")
        return 1
    except (OSError, IOError) as e:
        print()
        print(f"ERROR: {e}")
        return 1
    except RuntimeError as e:
        print()
        print(f"ERROR: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
