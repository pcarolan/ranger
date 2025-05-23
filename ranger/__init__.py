"""
This is the main module for the ranger project.
"""

from ranger.cli import CLI

__all__ = ['CLI']

# Expose the CLI instance for direct usage
cli = CLI()