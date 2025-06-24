# Core module for AI Interaction Tool
# Contains main dialog, configuration management, response formatting, and MCP handler

from .dialog import InputDialog
from .config import ConfigManager
from .response_formatter import (
    format_mixed_response, 
    format_text_only_response, 
    build_error_response,
    validate_response_data
)
from .mcp_handler import ai_interaction_tool, get_tool_description

__all__ = [
    'InputDialog', 
    'ConfigManager',
    'format_mixed_response',
    'format_text_only_response', 
    'build_error_response',
    'validate_response_data',
    'ai_interaction_tool',
    'get_tool_description'
] 