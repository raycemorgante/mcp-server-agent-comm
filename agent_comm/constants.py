"""
Constants and configuration for Agent Communication System
"""

import os
from pathlib import Path

# Paths
PACKAGE_DIR = Path(__file__).parent
SHARED_DATA_DIR = PACKAGE_DIR / "shared_data"
UI_DIR = PACKAGE_DIR / "ui"

# Shared JSON Files
CONVERSATIONS_FILE = SHARED_DATA_DIR / "conversations.json"
PENDING_CALLS_FILE = SHARED_DATA_DIR / "pending_calls.json"
AGENT_REGISTRY_FILE = SHARED_DATA_DIR / "agent_registry.json"
CONFIG_FILE = SHARED_DATA_DIR / "config.json"

# UI Configuration
UI_TITLE = "Agent Communication Controller"
UI_WIDTH = 1200  # Increased default size
UI_HEIGHT = 800

# Message Status
MESSAGE_STATUS = {
    "PENDING": "pending",
    "DELIVERED": "delivered",
    "READ": "read"
}

# Agent Types
AGENT_TYPES = {
    "CLAUDE": "claude",
    "CHATGPT": "chatgpt", 
    "GEMINI": "gemini",
    "COPILOT": "copilot",
    "CUSTOM": "custom"
}

# Default Agent Colors (for UI)
AGENT_COLORS = {
    "claude": "#FF6B6B",      # Red
    "chatgpt": "#4ECDC4",     # Teal  
    "gemini": "#45B7D1",      # Blue
    "copilot": "#96CEB4",     # Green
    "custom": "#FFEAA7"       # Yellow
}

# UI Styling
UI_STYLES = {
    "BACKGROUND": "#2C3E50",
    "TEXT": "#FFFFFF", 
    "BUTTON": "#3498DB",
    "BUTTON_HOVER": "#2980B9",
    "MESSAGE_BUBBLE": "#34495E"
}

# Tool Configuration
DEFAULT_TOOL_CONFIG = {
    "max_message_length": 5000,
    "max_conversation_history": 100,
    "auto_save_interval": 30,  # seconds
    "ui_update_interval": 1000  # milliseconds
}

# Ensure shared data directory exists
SHARED_DATA_DIR.mkdir(exist_ok=True) 