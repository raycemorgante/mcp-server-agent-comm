"""
Main Engine for Agent Communication MCP Tool
"""

import sys
from typing import Optional, Dict, Any

from .core.state_manager import StateManager
from .core.message_handler import MessageHandler
from .ui.controller_ui import show_controller_ui


def run_agent_comm():
    """
    Main entry point for agent communication tool
    This function will be called by MCP server
    """
    try:
        # Parse command line arguments if any
        args = sys.argv[1:] if len(sys.argv) > 1 else []
        
        # Default parameters
        agent_id = None
        message = None
        action = "communicate"
        
        # Parse arguments (simple format for now)
        # Expected format: agent_id [message] [action]
        if args:
            agent_id = args[0]
            if len(args) > 1:
                message = args[1]
            if len(args) > 2:
                action = args[2]
        
        # Process based on action
        if action == "send_message":
            return handle_send_message(agent_id, message)
        elif action == "check_messages":
            return handle_check_messages(agent_id)
        else:
            # Default: show UI for interactive communication
            return handle_interactive_communication(agent_id, message)
    
    except Exception as e:
        return f"Error in agent communication tool: {str(e)}"


def handle_send_message(from_agent: str, message: str) -> str:
    """Handle sending a message"""
    try:
        if not from_agent or not message:
            return "Error: Agent ID and message are required for sending"
        
        message_handler = MessageHandler()
        
        # Parse agent info
        from_agent_id, from_agent_name, from_agent_type = message_handler.parse_agent_id(from_agent)
        
        # Add to pending calls (waiting for user to route)
        state_manager = StateManager()
        state_manager.add_pending_call(from_agent_id, message)
        
        # Show UI to let user choose target
        target_agent = show_controller_ui()
        
        if target_agent:
            # Send message to target
            success, result = message_handler.send_message(
                from_agent_id, target_agent, message, 
                from_agent_name, from_agent_type
            )
            
            # Remove from pending calls
            state_manager.remove_pending_call(from_agent_id)
            
            return result
        else:
            # Remove from pending calls if cancelled
            state_manager.remove_pending_call(from_agent_id)
            return "Message sending cancelled by user"
    
    except Exception as e:
        return f"Error sending message: {str(e)}"


def handle_check_messages(agent_id: str) -> str:
    """Handle checking for messages"""
    try:
        if not agent_id:
            return "Error: Agent ID is required for checking messages"
        
        message_handler = MessageHandler()
        
        # Parse agent info
        agent_id_parsed, agent_name, agent_type = message_handler.parse_agent_id(agent_id)
        
        # Check for messages
        success, result = message_handler.check_messages(agent_id_parsed, agent_name, agent_type)
        
        return result
    
    except Exception as e:
        return f"Error checking messages: {str(e)}"


def handle_interactive_communication(agent_id: str = None, message: str = None) -> str:
    """Handle interactive communication via UI"""
    try:
        state_manager = StateManager()
        
        # Add to pending calls if agent provided
        if agent_id:
            state_manager.add_pending_call(agent_id, message)
        
        # Show UI
        target_agent = show_controller_ui()
        
        if target_agent and agent_id and message:
            # Send message
            message_handler = MessageHandler()
            agent_id_parsed, agent_name, agent_type = message_handler.parse_agent_id(agent_id)
            
            success, result = message_handler.send_message(
                agent_id_parsed, target_agent, message,
                agent_name, agent_type
            )
            
            # Remove from pending calls
            state_manager.remove_pending_call(agent_id_parsed)
            
            return result
        else:
            # Just show UI for monitoring
            if agent_id:
                state_manager.remove_pending_call(agent_id)
            return "Agent Communication UI closed"
    
    except Exception as e:
        return f"Error in interactive communication: {str(e)}"


# Alternative function signatures for flexibility
def agent_comm_send(from_agent: str, to_agent: str, message: str) -> str:
    """Send message directly between agents"""
    try:
        message_handler = MessageHandler()
        
        # Parse agent info
        from_agent_id, from_agent_name, from_agent_type = message_handler.parse_agent_id(from_agent)
        to_agent_id, _, _ = message_handler.parse_agent_id(to_agent)
        
        success, result = message_handler.send_message(
            from_agent_id, to_agent_id, message,
            from_agent_name, from_agent_type
        )
        
        return result
    
    except Exception as e:
        return f"Error in direct send: {str(e)}"


def agent_comm_check(agent_id: str) -> str:
    """Check messages for agent"""
    return handle_check_messages(agent_id)


def agent_comm_status() -> str:
    """Get system status"""
    try:
        state_manager = StateManager()
        message_handler = MessageHandler()
        
        # Get system info
        agents = state_manager.get_all_agents()
        pending_calls = state_manager.get_pending_calls()
        conversations = state_manager.get_all_conversations()
        
        # Format status
        status_lines = [
            "=== Agent Communication System Status ===",
            f"Total Agents: {len(agents)}",
            f"Pending Tool Calls: {len(pending_calls)}",
            f"Total Conversations: {len(conversations)}",
            ""
        ]
        
        if agents:
            status_lines.append("Registered Agents:")
            for agent_id, info in agents.items():
                status = info.get("status", "unknown")
                agent_type = info.get("type", "unknown")
                status_lines.append(f"  • {agent_id} ({agent_type}) - {status}")
            status_lines.append("")
        
        if pending_calls:
            status_lines.append("Pending Tool Calls:")
            for agent_id, call_info in pending_calls.items():
                timestamp = call_info.get("timestamp", "unknown")
                status_lines.append(f"  • {agent_id} - {timestamp}")
        
        return "\n".join(status_lines)
    
    except Exception as e:
        return f"Error getting status: {str(e)}"


# Main execution for testing
if __name__ == "__main__":
    result = run_agent_comm()
    print(result) 