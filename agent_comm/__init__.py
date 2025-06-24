# Agent Communication Package
# Multi-Agent Communication System via MCP

from .core.state_manager import StateManager
from .core.message_handler import MessageHandler
from .core.conversation import ConversationManager

# Main entry point
from .engine import run_agent_comm

__version__ = "1.0.0"
__author__ = "DemonVN"
__all__ = [
    # Core components
    'StateManager',
    'MessageHandler', 
    'ConversationManager',
    
    # Main entry point
    'run_agent_comm',
    'agent_comm_tool',
]

def agent_comm_tool(agent_id: str = None, message: str = None, action: str = "communicate"):
    """
    Main entry point for agent communication tool with MCP parameters
    
    Args:
        agent_id: ID of the calling agent
        message: Message content to send
        action: Action to perform (send_message, check_messages, communicate)
    """
    try:
        from .engine import handle_send_message, handle_check_messages, handle_interactive_communication
        
        # Process based on action
        if action == "send_message" and agent_id and message:
            return handle_send_message(agent_id, message)
        elif action == "check_messages" and agent_id:
            return handle_check_messages(agent_id)
        else:
            # Default: interactive communication
            return handle_interactive_communication(agent_id, message)
            
    except Exception as e:
        return f"Error in agent communication tool: {str(e)}" 