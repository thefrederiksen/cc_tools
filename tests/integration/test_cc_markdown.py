"""Integration tests for cc-markdown CLI.

These tests run the actual CLI tool and verify outputs.
"""

import pytest
import subprocess
import sys
from pathlib import Path

# Paths
FIXTURES_DIR = Path(__file__).parent / "fixtures"
OUTPUT_DIR = Path(__file__).parent / "output"

# Ensure output directory exists
OUTPUT_DIR.mkdir(exist_ok=True)


def run_cc-markdown(*args, check=True):
    """Run cc-markdown CLI and return result."""
    cmd = [sys.executable, "-m", "src.cli"] + list(args)
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent.parent / "src" / "cc-markdown",
    )
    if check and result.returncode != 0:
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
    return result


class TestCLIBasic:
    """Test basic CLI operations."""

    def test_version(self):
        """Test --version flag."""
        result = run_cc-markdown("--version")
        assert result.returncode == 0
        assert "cc-markdown" in result.stdout.lower() or "0." in result.stdout

    def test_help(self):
        """Test --help flag."""
        result = run_cc-markdown("--help")
        assert result.returncode == 0
        assert "markdown" in result.stdout.lower()

    def test_list_themes(self):
        """Test --themes flag."""
        result = run_cc-markdown("--themes")
        assert result.returncode == 0
        # Check for known themes
        assert "paper" in result.stdout.lower()
        assert "boardroom" in result.stdout.lower()


class TestMarkdownToHTML:
    """Test markdown to HTML conversion."""

    def test_basic_to_html(self):
        """Convert basic.md to HTML."""
        input_file = FIXTURES_DIR / "basic.md"
        output_file = OUTPUT_DIR / "basic.html"

        result = run_cc-markdown(str(input_file), "-o", str(output_file))

        assert result.returncode == 0
        assert output_file.exists()

        content = output_file.read_text()
        assert "<!DOCTYPE html>" in content
        assert "Basic Markdown Test" in content
        assert "<h1>" in content
        assert "<table>" in content

    def test_advanced_to_html(self):
        """Convert advanced.md to HTML."""
        input_file = FIXTURES_DIR / "advanced.md"
        output_file = OUTPUT_DIR / "advanced.html"

        result = run_cc-markdown(str(input_file), "-o", str(output_file))

        assert result.returncode == 0
        assert output_file.exists()

        content = output_file.read_text()
        assert "checkbox" in content.lower() or "task" in content.lower()


class TestMarkdownToPDF:
    """Test markdown to PDF conversion."""

    @pytest.mark.slow
    def test_basic_to_pdf(self):
        """Convert basic.md to PDF."""
        input_file = FIXTURES_DIR / "basic.md"
        output_file = OUTPUT_DIR / "basic.pdf"

        result = run_cc-markdown(str(input_file), "-o", str(output_file))

        assert result.returncode == 0
        assert output_file.exists()
        assert output_file.stat().st_size > 0  # PDF should have content

    @pytest.mark.slow
    def test_pdf_with_theme(self):
        """Convert with boardroom theme to PDF."""
        input_file = FIXTURES_DIR / "report.md"
        output_file = OUTPUT_DIR / "report_boardroom.pdf"

        result = run_cc-markdown(
            str(input_file),
            "-o", str(output_file),
            "--theme", "boardroom"
        )

        assert result.returncode == 0
        assert output_file.exists()

    @pytest.mark.slow
    def test_all_themes_pdf(self):
        """Test all themes generate valid PDFs."""
        themes = ["paper", "boardroom", "terminal", "spark", "thesis", "obsidian", "blueprint"]
        input_file = FIXTURES_DIR / "basic.md"

        for theme in themes:
            output_file = OUTPUT_DIR / f"theme_{theme}.pdf"
            result = run_cc-markdown(
                str(input_file),
                "-o", str(output_file),
                "--theme", theme
            )
            assert result.returncode == 0, f"Theme {theme} failed"
            assert output_file.exists(), f"Theme {theme} output missing"


class TestMarkdownToWord:
    """Test markdown to Word conversion."""

    def test_basic_to_docx(self):
        """Convert basic.md to DOCX."""
        input_file = FIXTURES_DIR / "basic.md"
        output_file = OUTPUT_DIR / "basic.docx"

        result = run_cc-markdown(str(input_file), "-o", str(output_file))

        assert result.returncode == 0
        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_report_to_docx(self):
        """Convert report.md to DOCX."""
        input_file = FIXTURES_DIR / "report.md"
        output_file = OUTPUT_DIR / "report.docx"

        result = run_cc-markdown(str(input_file), "-o", str(output_file))

        assert result.returncode == 0
        assert output_file.exists()


class TestErrorHandling:
    """Test error handling."""

    def test_missing_input_file(self):
        """Test error for missing input file."""
        result = run_cc-markdown("nonexistent.md", "-o", "output.pdf", check=False)
        assert result.returncode != 0

    def test_invalid_theme(self):
        """Test error for invalid theme."""
        input_file = FIXTURES_DIR / "basic.md"
        output_file = OUTPUT_DIR / "invalid_theme.pdf"

        result = run_cc-markdown(
            str(input_file),
            "-o", str(output_file),
            "--theme", "nonexistent_theme",
            check=False
        )
        assert result.returncode != 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
