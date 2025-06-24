#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Server dành riêng cho Agent 2
"""

from mcp.server.fastmcp import FastMCP
from agent_comm.agent_chat_tools import agent_chat_2_tool

# Tạo MCP server cho Agent 2
mcp = FastMCP("Agent 2 Communication")

# Add tool cho Agent 2
mcp.add_tool(agent_chat_2_tool)

if __name__ == "__main__":
    # Chạy server với transport=stdio
    mcp.run(transport="stdio") 