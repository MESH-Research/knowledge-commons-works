# Part of Knowledge Commons Works
# Copyright (C) 2024-2025 MESH Research
#
# KCWorks is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Pytest plugin for displaying live test status during execution."""

import pytest


class LiveTestStatusPlugin:
    """Pytest plugin to display running pass/fail percentages during tests.

    This plugin displays a live status bar at the bottom of the terminal:
    - Pass percentage and count
    - Fail percentage and count
    - Skip count
    - Error count

    It works alongside -vv to show progress while verbose output scrolls.
    The status bar remains fixed at the bottom using terminal scroll regions.
    """

    def __init__(self):
        """Initialize the plugin counters."""
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.errors = 0
        self.xfailed = 0
        self.xpassed = 0
        self.total = 0
        self.total_discovered = 0  # Total number of tests discovered during collection
        self.terminal = None
        self.is_tty = False
        self._status_lines = 2  # Number of lines to reserve at bottom
        self._terminal_height = 24  # Default, will be updated

    def pytest_configure(self, config):
        """Configure the plugin and check if we're in a TTY."""
        import os
        import sys

        self.terminal = config.pluginmanager.get_plugin("terminalreporter")
        self.is_tty = hasattr(sys.stderr, "isatty") and sys.stderr.isatty()

        if self.is_tty:
            # Get terminal height
            try:
                self._terminal_height = os.get_terminal_size().lines
            except (OSError, AttributeError):
                self._terminal_height = 24

            # Set up scroll region (leave bottom lines for status)
            self._setup_scroll_region()

    def _setup_scroll_region(self):
        """Set up terminal scroll region to keep status bar at bottom."""
        import sys

        # Set scroll region (top to height - status_lines)
        # Line numbers are 1-indexed
        scroll_bottom = self._terminal_height - self._status_lines

        # Set up the scroll region
        sys.stderr.write(f"\033[1;{scroll_bottom}r")  # Set scroll region

        # Draw separator and initial status at the bottom (outside scroll region)
        sys.stderr.write(f"\033[{self._terminal_height - 1};1H")  # Separator line
        sys.stderr.write("\033[2K")  # Clear line
        sys.stderr.write("=" * 80)
        sys.stderr.write(f"\033[{self._terminal_height};1H")  # Status line
        sys.stderr.write("\033[2K")  # Clear line
        sys.stderr.write("Initializing tests...")

        # Move cursor back to top of scrolling region
        sys.stderr.write("\033[1;1H")  # Move cursor to top-left
        sys.stderr.flush()

    def _restore_scroll_region(self):
        """Restore normal terminal scrolling."""
        import sys

        sys.stderr.write("\033[r")  # Reset scroll region to full screen
        sys.stderr.write(f"\033[{self._terminal_height - 1};1H")  # Move to separator
        sys.stderr.write("\033[2K\n")  # Clear separator
        sys.stderr.write("\033[2K\n")  # Clear status line
        sys.stderr.flush()

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_logreport(self, report):
        """Update counters after each test phase."""
        yield

        # Only count the 'call' phase to avoid counting setup/teardown
        if report.when == "call":
            self.total += 1

            if report.passed:
                self.passed += 1
            elif report.failed:
                self.failed += 1
            elif report.skipped:
                self.skipped += 1

        # Count errors from any phase
        elif report.when in ("setup", "teardown"):
            if report.failed:
                self.errors += 1
                self.total += 1

        # Handle xfail and xpass
        if hasattr(report, "wasxfail"):
            if report.skipped:
                self.xfailed += 1
            elif report.passed:
                self.xpassed += 1

        self._display_status()

    def _display_status(self):
        """Display the current test status in fixed position at bottom."""
        if not self.is_tty:
            # For non-TTY (e.g., CI), print periodically
            if self.total > 0 and self.total % 10 == 0:
                status_parts = []
                pass_pct = (self.passed / self.total * 100) if self.total else 0
                if self.passed > 0:
                    status_parts.append(f"✓ {self.passed} passed ({pass_pct:.1f}%)")
                if self.failed > 0:
                    fail_pct = self.failed / self.total * 100
                    status_parts.append(f"✗ {self.failed} failed ({fail_pct:.1f}%)")
                status_msg = " | ".join(status_parts) if status_parts else "Starting..."
                # Show progress if we know the total discovered count
                if self.total_discovered > 0:
                    total_msg = f"[{self.total}/{self.total_discovered} tests]"
                else:
                    total_msg = f"[{self.total} tests]"
                if self.terminal:
                    self.terminal.write_line(f"\n{total_msg} {status_msg}\n")
            return

        # Calculate percentages
        pass_pct = (self.passed / self.total * 100) if self.total else 0
        fail_pct = (self.failed / self.total * 100) if self.total else 0

        # Build status message with color codes
        status_parts = []

        if self.passed > 0:
            status_parts.append(
                f"\033[32m✓ {self.passed} passed ({pass_pct:.1f}%)\033[0m"
            )

        if self.failed > 0:
            status_parts.append(
                f"\033[31m✗ {self.failed} failed ({fail_pct:.1f}%)\033[0m"
            )

        if self.errors > 0:
            status_parts.append(f"\033[31m⚠ {self.errors} errors\033[0m")

        if self.skipped > 0:
            status_parts.append(f"\033[33m⊘ {self.skipped} skipped\033[0m")

        if self.xfailed > 0:
            status_parts.append(f"\033[33m⊘ {self.xfailed} xfailed\033[0m")

        if self.xpassed > 0:
            status_parts.append(f"\033[32m✓ {self.xpassed} xpassed\033[0m")

        status_msg = " | ".join(status_parts) if status_parts else "Running tests..."
        # Show progress if we know the total discovered count
        if self.total_discovered > 0:
            total_msg = f"\033[1m[{self.total}/{self.total_discovered} tests]\033[0m"
        else:
            total_msg = f"\033[1m[{self.total} tests]\033[0m"

        # Update the fixed status line at bottom
        import sys

        status_line_pos = self._terminal_height
        # Use DEC save/restore which works better with scroll regions
        sys.stderr.write("\0337")  # Save cursor (DEC)
        sys.stderr.write(f"\033[{status_line_pos};1H")  # Move to status line
        sys.stderr.write("\033[K")  # Clear line
        sys.stderr.write(f"{total_msg} {status_msg}")
        sys.stderr.write("\0338")  # Restore cursor (DEC)
        sys.stderr.flush()

    def pytest_collection_finish(self, session):
        """Capture the total number of discovered tests after collection."""
        # Store the total number of collected test items
        self.total_discovered = len(session.items)
        # Update display to show we know the total now
        self._display_status()

    def pytest_sessionfinish(self, session):
        """Restore terminal when session finishes."""
        if self.is_tty:
            self._restore_scroll_region()


def pytest_addoption(parser):
    """Add command-line options for the live status plugin."""
    parser.addoption(
        "--live-status",
        action="store_true",
        default=True,
        help="Show live test status updates (default: enabled)",
    )
    parser.addoption(
        "--no-live-status",
        "-L",
        action="store_false",
        dest="live_status",
        help="Disable live test status updates",
    )


def pytest_configure(config):
    """Register the live status plugin if enabled."""
    if config.getoption("live_status", True):
        config.pluginmanager.register(LiveTestStatusPlugin(), "live_status")
