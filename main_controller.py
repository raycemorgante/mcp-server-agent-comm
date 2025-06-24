#!/usr/bin/env python3
"""
Main Controller for Agent Communication System

This is the external controller that user runs to manage message flow
between Agent Chat 1 and Agent Chat 2 tools.

Usage:
    python main_controller.py

The controller UI will show:
- Waiting agents (from agent_chat_1_tool and agent_chat_2_tool calls)
- Pending messages in queue
- Controls to deliver messages between agents
"""

import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from agent_comm.agent_chat_tools import agent_controller_tool
    
    if __name__ == "__main__":
        print("🚀 Starting Agent Communication Controller...")
        print("This UI allows you to control message flow between waiting agents.")
        print("Close the UI window when finished.")
        print("-" * 60)
        
        # Run the controller tool
        result = agent_controller_tool()
        
        print(f"\nController result: {result}")
        print("Controller session ended.")
        
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure you're in the correct directory with agent_comm package.")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ Error running controller: {e}")
    sys.exit(1) 