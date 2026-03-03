#!/usr/bin/env python3
"""
ShellSpark — Your Intelligent Terminal Companion
Entry point for `python -m shellspark`.
"""

import sys
from shellspark.cli.app import main

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        from shellspark.cli.ui import console
        console.print("\n[dim]👋 Goodbye![/]")
        sys.exit(130)
