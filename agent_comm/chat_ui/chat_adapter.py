"""
Chat Adapter - Bridge between agent_comm and ai_interaction dialog
"""

import os
import sys
from typing import Optional, Dict, Any
from PyQt5.QtWidgets import QMessageBox

def show_ai_chat_dialog(parent=None) -> Optional[tuple]:
    """
    Show AI Chat dialog with full ai_interaction functionality
    Returns the result text and continue flag if available
    """
    try:
        # Import the real ai_interaction dialog
        from .core.dialog import InputDialog
        
        # Create and show dialog
        dialog = InputDialog()
        
        # Show as modal dialog
        result = dialog.exec_()
        
        if result == dialog.Accepted:
            # Get the result directly from the dialog that was just shown
            try:
                # Get result from dialog attributes which already contain the correct format
                if hasattr(dialog, 'result_text') and hasattr(dialog, 'result_continue'):
                    message = dialog.result_text
                    continue_chat = dialog.result_continue
                    if message:
                        # If message is JSON (from ai_interaction with images), preserve original format for agent_chat tools
                        try:
                            import json
                            if message.strip().startswith('{'):
                                message_dict = json.loads(message)
                                attached_images = message_dict.get("attached_images", [])
                                
                                # If has images, return original mixed format (JSON + tags) so agent_chat tools can process images
                                if attached_images:
                                    # Build mixed format: JSON + remaining tags
                                    json_part = message.strip()
                                    if json_part.endswith('\n'):
                                        json_part = json_part.rstrip('\n')
                                    
                                    # Add continue_chat tag
                                    mixed_format = json_part + f"\n\n<AI_INTERACTION_CONTINUE_CHAT>{str(continue_chat).lower()}</AI_INTERACTION_CONTINUE_CHAT>"
                                    return mixed_format, continue_chat
                                
                                # No images - parse and convert to clean text format 
                                user_text = message_dict.get("text_content", message_dict.get("text", ""))
                                attached_files = message_dict.get("attached_files", [])
                                
                                # Build clean text format
                                full_response_text = user_text
                                
                                if attached_files:
                                    full_response_text += "\n\n<AI_INTERACTION_ATTACHED_FILES>\n"
                                    
                                    folders = []
                                    files = []
                                    
                                    for file_info in attached_files:
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
                                
                                full_response_text += f"\n\n<AI_INTERACTION_CONTINUE_CHAT>{str(continue_chat).lower()}</AI_INTERACTION_CONTINUE_CHAT>"
                                
                                return full_response_text, continue_chat
                            else:
                                # Already clean format
                                return message, continue_chat
                        except (json.JSONDecodeError, TypeError):
                            # Not JSON or failed to parse - return as is
                            return message, continue_chat
                    
            except Exception as dialog_error:
                # Ultimate fallback
                pass
            
        return None, False
        
    except ImportError as e:
        # Fallback to simplified dialog if ai_interaction components fail
        try:
            from .simple_dialog import show_simple_ai_chat_dialog
            message, continue_chat = show_simple_ai_chat_dialog(parent)
            if message:
                return message, continue_chat
            return None, False
        except:
            QMessageBox.critical(
                parent,
                "AI Chat Error", 
                f"Failed to load AI Chat components:\n{str(e)}\n\nPlease ensure all dependencies are installed."
            )
            return None, False
        
    except Exception as e:
        QMessageBox.critical(
            parent,
            "AI Chat Error",
            f"Error opening AI Chat:\n{str(e)}"
        )
        return None, False 