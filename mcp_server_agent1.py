#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Server dành riêng cho Agent 1
"""

from mcp.server.fastmcp import FastMCP
from agent_comm.agent_chat_tools import agent_chat_1_tool

# Tạo MCP server cho Agent 1
mcp = FastMCP("Agent 1 Communication")

# Add tool cho Agent 1
mcp.add_tool(agent_chat_1_tool)

if __name__ == "__main__":
    # Chạy server với transport=stdio
    mcp.run(transport="stdio") 