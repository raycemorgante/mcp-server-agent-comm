#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MCP Server for group chat among file-specific agents.

This server exposes the ``agent_group_chat_tool`` and can optionally spawn
multiple agent processes on start-up. The list of agent Python files can be
provided as command-line arguments or through the environment variable
``GROUP_CHAT_AGENT_FILES`` (comma-separated). Each file is launched as a
separate subprocess using the current Python interpreter.
"""

import argparse
import os
import subprocess
import sys
from typing import List

from mcp.server.fastmcp import FastMCP
from agent_comm.agent_chat_tools import agent_group_chat_tool


def _parse_agent_files() -> List[str]:
    """Return agent file paths from CLI arguments or environment variable."""
    parser = argparse.ArgumentParser(description="Run MCP group chat server")
    parser.add_argument(
        "agent_files",
        nargs="*",
        help="Paths to agent Python files to spawn on start-up",
    )
    args = parser.parse_args()

    files = args.agent_files
    if not files:
        env_value = os.getenv("GROUP_CHAT_AGENT_FILES", "")
        if env_value:
            # Support comma or os.pathsep separated values
            for part in env_value.replace(os.pathsep, ",").split(","):
                part = part.strip()
                if part:
                    files.append(part)
    return files


def _spawn_agents(files: List[str]) -> List[subprocess.Popen]:
    """Spawn each Python file as a subprocess."""
    processes: List[subprocess.Popen] = []
    for path in files:
        if os.path.isfile(path) and path.endswith(".py"):
            processes.append(subprocess.Popen([sys.executable, path]))
    return processes


# Instantiate FastMCP and register the group chat tool
mcp = FastMCP("Agent Group Chat")
mcp.add_tool(agent_group_chat_tool)


if __name__ == "__main__":
    agent_files = _parse_agent_files()
    spawned_processes = _spawn_agents(agent_files)
    try:
        mcp.run(transport="stdio")
    finally:
        for proc in spawned_processes:
            proc.terminate()
