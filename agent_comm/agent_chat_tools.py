"""
Agent Chat Tools - Separate tools for Agent 1, Agent 2, and Controller
"""

from typing import Optional
from .core.flow_manager import FlowManager

# Import MCP types for image handling
try:
    from mcp.types import TextContent
    from mcp.server.fastmcp.utilities.types import Image as MCPImage
    from typing import List, Union
    import base64
    MCP_AVAILABLE = True
except ImportError:
    from typing import List, Union
    MCP_AVAILABLE = False


def _parse_mixed_format_message(delivered_message: str):
    """
    Parse mixed format message (JSON + ai_interaction tags) and return clean format
    
    Args:
        delivered_message: Mixed format message with JSON + tags
        
    Returns:
        Either clean text string or List[TextContent + MCPImage] if images present
    """
    try:
        import json
        message_content = delivered_message.strip()
        
        # Check if message contains JSON at the beginning
        if message_content.startswith('{'):
            # Find the end of JSON object
            brace_count = 0
            json_end_pos = -1
            
            for i, char in enumerate(message_content):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        json_end_pos = i + 1
                        break
            
            if json_end_pos > 0:
                # Parse JSON part
                json_part = message_content[:json_end_pos]
                remaining_part = message_content[json_end_pos:].strip()
                
                try:
                    message_dict = json.loads(json_part)
                    user_text = message_dict.get("text_content", message_dict.get("text", ""))
                    attached_files = message_dict.get("attached_files", [])
                    attached_images = message_dict.get("attached_images", [])
                    
                    # Extract continue_chat from tags part if present
                    continue_chat = False
                    if "<AI_INTERACTION_CONTINUE_CHAT>true</AI_INTERACTION_CONTINUE_CHAT>" in remaining_part:
                        continue_chat = True
                    elif "<AI_INTERACTION_CONTINUE_CHAT>false</AI_INTERACTION_CONTINUE_CHAT>" in remaining_part:
                        continue_chat = False
                    else:
                        # Fallback to JSON value
                        continue_chat = message_dict.get("continue_chat", False)
                    
                    # Extract source from tags part if present (default to "admin" for delivered messages)
                    source = "admin"  # Default for messages delivered through controller
                    if "<AI_INTERACTION_SOURCE>agent</AI_INTERACTION_SOURCE>" in remaining_part:
                        source = "agent"
                    elif "<AI_INTERACTION_SOURCE>admin</AI_INTERACTION_SOURCE>" in remaining_part:
                        source = "admin"
                    
                    # Check if we have images - return List[TextContent + MCPImage] like ai_interaction
                    if attached_images:
                        return _format_mixed_response_with_images(user_text, attached_files, attached_images, continue_chat, source)
                    
                    # Build clean text format for text-only
                    full_response_text = user_text
                    
                    if attached_files:
                        full_response_text += "\n\n<AI_INTERACTION_ATTACHED_FILES>\n"
                        
                        folders = []
                        files = []
                        
                        for file_info in attached_files:
                            if isinstance(file_info, dict):
                                relative_path = file_info.get('relative_path', 'unknown_path')
                                item_type = file_info.get('type', 'file')
                                
                                if item_type.lower() == 'folder':
                                    folders.append(relative_path)
                                else:
                                    files.append(relative_path)
                        
                        if folders:
                            full_response_text += "FOLDERS:\n"
                            for folder in folders:
                                full_response_text += f"- {folder}\n"
                            full_response_text += "\n"
                        
                        if files:
                            full_response_text += "FILES:\n"
                            for file in files:
                                full_response_text += f"- {file}\n"
                            full_response_text += "\n"
                        
                        full_response_text += "</AI_INTERACTION_ATTACHED_FILES>\n"
                        
                        # Add workspace info if available
                        if attached_files and isinstance(attached_files[0], dict):
                            workspace_name = attached_files[0].get('workspace_name', '')
                            if workspace_name:
                                full_response_text += f"\n<AI_INTERACTION_WORKSPACE>{workspace_name}</AI_INTERACTION_WORKSPACE>"
                    
                    full_response_text += f"\n\n<AI_INTERACTION_SOURCE>{source}</AI_INTERACTION_SOURCE>"
                    full_response_text += f"\n<AI_INTERACTION_CONTINUE_CHAT>{str(continue_chat).lower()}</AI_INTERACTION_CONTINUE_CHAT>"
                    
                    return full_response_text
                    
                except json.JSONDecodeError:
                    pass
        
        # If no JSON found or parsing failed, return original message
        return delivered_message
        
    except Exception:
        # Any error, return original message
        return delivered_message


def _format_mixed_response_with_images(user_text: str, attached_files: list, attached_images: list, continue_chat: bool, source: str = "admin"):
    """
    Format mixed response with images like ai_interaction tool
    
    Args:
        user_text: User message text
        attached_files: List of attached files
        attached_images: List of attached images  
        continue_chat: Continue chat flag
        
    Returns:
        List[TextContent + MCPImage] like ai_interaction tool
    """
    if not MCP_AVAILABLE:
        # Fallback to text-only if MCP not available
        return _format_text_only_fallback(user_text, attached_files, continue_chat, source)
    
    response_items = []
    
    # Build text content with tags (same as ai_interaction)
    full_text_content = user_text
    
    if attached_files:
        full_text_content += "\n\n<AI_INTERACTION_ATTACHED_FILES>\n"
        
        folders = []
        files = []
        
        for file_info in attached_files:
            if isinstance(file_info, dict):
                relative_path = file_info.get('relative_path', 'unknown_path')
                item_type = file_info.get('type', 'file')
                
                if item_type.lower() == 'folder':
                    folders.append(relative_path)
                else:
                    files.append(relative_path)
        
        if folders:
            full_text_content += "FOLDERS:\n"
            for folder in folders:
                full_text_content += f"- {folder}\n"
            full_text_content += "\n"
        
        if files:
            full_text_content += "FILES:\n"
            for file in files:
                full_text_content += f"- {file}\n"
            full_text_content += "\n"
        
        full_text_content += "</AI_INTERACTION_ATTACHED_FILES>\n"
        
        # Add workspace info if available
        if attached_files and isinstance(attached_files[0], dict):
            workspace_name = attached_files[0].get('workspace_name', '')
            if workspace_name:
                full_text_content += f"\n<AI_INTERACTION_WORKSPACE>{workspace_name}</AI_INTERACTION_WORKSPACE>"
    
    full_text_content += f"\n\n<AI_INTERACTION_SOURCE>{source}</AI_INTERACTION_SOURCE>"
    full_text_content += f"\n<AI_INTERACTION_CONTINUE_CHAT>{str(continue_chat).lower()}</AI_INTERACTION_CONTINUE_CHAT>"
    
    # Add text content
    response_items.append(TextContent(type="text", text=full_text_content))
    
    # Add images as MCPImage objects (same as ai_interaction)
    if attached_images:
        mcp_images = _process_images(attached_images)
        response_items.extend(mcp_images)
    
    return response_items


def _process_images(images_data: list):
    """
    Process image data and convert to MCP Image objects (copied from ai_interaction)
    """
    mcp_images = []
    
    for i, img in enumerate(images_data, 1):
        try:
            if not img.get("base64_data"):
                continue
            
            # Decode base64 to raw bytes
            if isinstance(img["base64_data"], str):
                image_bytes = base64.b64decode(img["base64_data"])
            else:
                continue
            
            if len(image_bytes) == 0:
                continue
            
            # Determine format from media_type or filename
            media_type = img.get("media_type", "image/png")
            filename = img.get("filename", "image.png")
            
            if "jpeg" in media_type or "jpg" in media_type or filename.lower().endswith(('.jpg', '.jpeg')):
                image_format = 'jpeg'
            elif "gif" in media_type or filename.lower().endswith('.gif'):
                image_format = 'gif'
            else:
                image_format = 'png'  # Default to PNG
            
            # Create MCPImage with raw bytes
            mcp_image = MCPImage(data=image_bytes, format=image_format)
            mcp_images.append(mcp_image)
            
        except Exception as e:
            import sys
            print(f"Error processing image {i}: {e}", file=sys.stderr)
            continue
    
    return mcp_images


def _format_text_only_fallback(user_text: str, attached_files: list, continue_chat: bool, source: str = "admin") -> str:
    """
    Fallback to text-only format when MCP not available
    """
    full_response_text = user_text
    
    if attached_files:
        full_response_text += "\n\n<AI_INTERACTION_ATTACHED_FILES>\n"
        
        folders = []
        files = []
        
        for file_info in attached_files:
            if isinstance(file_info, dict):
                relative_path = file_info.get('relative_path', 'unknown_path')
                item_type = file_info.get('type', 'file')
                
                if item_type.lower() == 'folder':
                    folders.append(relative_path)
                else:
                    files.append(relative_path)
        
        if folders:
            full_response_text += "FOLDERS:\n"
            for folder in folders:
                full_response_text += f"- {folder}\n"
            full_response_text += "\n"
        
        if files:
            full_response_text += "FILES:\n"
            for file in files:
                full_response_text += f"- {file}\n"
            full_response_text += "\n"
        
        full_response_text += "</AI_INTERACTION_ATTACHED_FILES>\n"
        
        # Add workspace info if available
        if attached_files and isinstance(attached_files[0], dict):
            workspace_name = attached_files[0].get('workspace_name', '')
            if workspace_name:
                full_response_text += f"\n<AI_INTERACTION_WORKSPACE>{workspace_name}</AI_INTERACTION_WORKSPACE>"
    
    full_response_text += f"\n\n<AI_INTERACTION_SOURCE>{source}</AI_INTERACTION_SOURCE>"
    full_response_text += f"\n<AI_INTERACTION_CONTINUE_CHAT>{str(continue_chat).lower()}</AI_INTERACTION_CONTINUE_CHAT>"
    
    return full_response_text


def _format_ai_interaction_response(message: str, continue_chat: bool = False, 
                                  workspace: str = "Utils", files: list = None, 
                                  folders: list = None, source: str = "admin") -> str:
    """
    Format response in ai_interaction format (exact same as ai_interaction tool engine.py)
    
    Args:
        message: Main message content
        continue_chat: Whether to continue chat
        workspace: Workspace name
        files: List of files to attach
        folders: List of folders to attach
    
    Returns:
        Formatted ai_interaction response matching ai_interaction tool format
    """
    # Start with clean user content (same as ai_interaction engine.py)
    full_response_text = message
    
    # Add attached files using collision-proof structured format (copied from engine.py)
    if files or folders:
        full_response_text += "\n\n<AI_INTERACTION_ATTACHED_FILES>\n"
        
        # Output structured sections (same order as engine.py)
        if folders:
            full_response_text += "FOLDERS:\n"
            for folder in folders:
                full_response_text += f"- {folder}\n"
            full_response_text += "\n"
        
        if files:
            full_response_text += "FILES:\n"
            for file in files:
                full_response_text += f"- {file}\n"
            full_response_text += "\n"
        
        full_response_text += "</AI_INTERACTION_ATTACHED_FILES>\n"
        
        # Add workspace info (same as engine.py)
        if workspace:
            full_response_text += f"\n<AI_INTERACTION_WORKSPACE>{workspace}</AI_INTERACTION_WORKSPACE>"
    
    # Add control tags at the end (same as engine.py)
    full_response_text += f"\n\n<AI_INTERACTION_SOURCE>{source}</AI_INTERACTION_SOURCE>"
    full_response_text += f"\n<AI_INTERACTION_CONTINUE_CHAT>{str(continue_chat).lower()}</AI_INTERACTION_CONTINUE_CHAT>"
    
    return full_response_text


def agent_chat_1_tool(agent_id: str, message: str) -> Union[str, List]:
    """
    Agent Chat 1 Tool - For any Agent 1
    
    Args:
        agent_id: ID of Agent 1 (e.g., "agent_001")
        message: Message to send (required)
    
    Returns:
        Message received from Agent 2 or status in ai_interaction format
    """
    try:
        flow_manager = FlowManager()
        
        # Register as waiting agent (all agent messages go to queue)
        waiting_id = flow_manager.register_waiting_agent("agent_chat_1", agent_id, message)
        
        # Wait for message delivery from controller (infinite wait - no timeout)
        delivered_message = flow_manager.wait_for_delivery(waiting_id, timeout=None)
        
        # Clean up waiting state
        flow_manager.remove_waiting_agent(waiting_id)
        
        if delivered_message:
            # Parse mixed format message (JSON + ai_interaction tags) and return clean format
            return _parse_mixed_format_message(delivered_message)
        else:
            # This should never happen with infinite wait, but keeping for safety
            return _format_ai_interaction_response(
                "Unexpected error: No message received.",
                continue_chat=False
            )
            
    except Exception as e:
        # Return error in ai_interaction format
        return _format_ai_interaction_response(
            f"Error in Agent Chat 1: {str(e)}",
            continue_chat=False
        )


def agent_chat_2_tool(agent_id: str, message: str) -> Union[str, List]:
    """
    Agent Chat 2 Tool - For any Agent 2
    
    Args:
        agent_id: ID of Agent 2 (e.g., "agent_002") 
        message: Message to send (required)
    
    Returns:
        Message received from Agent 1 or status in ai_interaction format
    """
    try:
        flow_manager = FlowManager()
        
        # Register as waiting agent (all agent messages go to queue)
        waiting_id = flow_manager.register_waiting_agent("agent_chat_2", agent_id, message)
        
        # Wait for message delivery from controller (infinite wait - no timeout)
        delivered_message = flow_manager.wait_for_delivery(waiting_id, timeout=None)
        
        # Clean up waiting state
        flow_manager.remove_waiting_agent(waiting_id)
        
        if delivered_message:
            # Parse mixed format message (JSON + ai_interaction tags) and return clean format
            return _parse_mixed_format_message(delivered_message)
        else:
            # This should never happen with infinite wait, but keeping for safety
            return _format_ai_interaction_response(
                "Unexpected error: No message received.",
                continue_chat=False
            )
            
    except Exception as e:
        # Return error in ai_interaction format
        return _format_ai_interaction_response(
            f"Error in Agent Chat 2: {str(e)}",
            continue_chat=False
        )


def agent_controller_tool() -> str:
    """
    Agent Controller Tool - Main UI for User to control message flow
    
    Returns:
        Result of user interaction
    """
    try:
        from .ui.controller_ui import show_controller_ui
        
        result = show_controller_ui()
        
        if result:
            return f"Controller action completed: {result}"
        else:
            return "Controller UI closed without action."
            
    except Exception as e:
        return f"Error in Agent Controller: {str(e)}"


# Convenience functions for testing
def get_flow_status() -> str:
    """Get current flow status for debugging"""
    try:
        flow_manager = FlowManager()
        data = flow_manager.get_controller_data()
        
        waiting_count = len(data["waiting_agents"])
        queue_count = len(data["message_queue"])
        
        status_lines = [
            "=== Agent Chat Flow Status ===",
            f"Waiting Agents: {waiting_count}",
            f"Pending Messages: {queue_count}",
            f"Last Update: {data['timestamp']}",
            ""
        ]
        
        if data["waiting_agents"]:
            status_lines.append("Waiting Agents:")
            for waiting_id, agent_data in data["waiting_agents"].items():
                agent_tool = agent_data.get("agent_tool", "unknown")
                agent_id = agent_data.get("agent_id", "unknown")
                status = agent_data.get("status", "unknown")
                status_lines.append(f"  • {waiting_id}: {agent_tool} ({agent_id}) - {status}")
            status_lines.append("")
        
        if data["message_queue"]:
            status_lines.append("Message Queue:")
            for msg in data["message_queue"]:
                from_agent = msg.get("from_agent", "unknown")
                delivered = "✓" if msg.get("delivered", False) else "⏳"
                message_preview = msg.get("message", "")[:50]
                status_lines.append(f"  {delivered} From {from_agent}: {message_preview}...")
        
        return "\n".join(status_lines)
        
    except Exception as e:
        return f"Error getting flow status: {str(e)}"


def cleanup_flow_data() -> str:
    """Clean up old flow data"""
    try:
        flow_manager = FlowManager()
        flow_manager.cleanup_old_data(hours=1)  # Clean data older than 1 hour
        return "Flow data cleanup completed."
        
    except Exception as e:
        return f"Error cleaning up flow data: {str(e)}"


def clear_all_flow_data() -> str:
    """Clear ALL flow data - complete reset"""
    try:
        flow_manager = FlowManager()
        flow_manager.clear_all_data()
        return "All flow data cleared successfully."
        
    except Exception as e:
        return f"Error clearing all flow data: {str(e)}" 