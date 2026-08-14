"""Sense organs. Each observer turns a public feed into timestamped observations.

An observer may only read. It writes into the store and nowhere else.
"""

from .mcp_registry import McpRegistry
from .github_skills import GithubSkills

OBSERVERS = [McpRegistry, GithubSkills]

__all__ = ["McpRegistry", "GithubSkills", "OBSERVERS"]
