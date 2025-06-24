# Main engine for AI Interaction Tool
# Refactored version - uses components from separate modules
from PyQt5 import QtWidgets, QtGui
import sys
import json
from .core.dialog import InputDialog

# Legacy classes for backward compatibility (now imported from separate modules)
from .ui.file_tree import FileSystemModel, FileTreeView, FileTreeDelegate
from .ui.file_dialog import FileAttachDialog

def run_ui(*args, **kwargs):
    """
    Hàm chính để chạy giao diện người dùng và trả về kết quả.
    Đây là entry point chính cho AI Interaction Tool.
    """
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    
    # Thiết lập font mặc định cho toàn ứng dụng
    font = QtGui.QFont("Segoe UI", 10)
    app.setFont(font)
    
    text, continue_chat, ok = InputDialog.getText()

    if ok:
        # Phân tích nội dung từ dialog
        try:
            # Parse JSON từ kết quả của dialog
            result_dict = json.loads(text)
            user_text = result_dict.get("text", "")
            attached_files = result_dict.get("attached_files", [])
            attached_images = result_dict.get("attached_images", [])
            language = result_dict.get("language", "vi")  # Mặc định tiếng Việt
            # ====== THINKING LOGIC COMPLETELY REMOVED - Natural Behavior ======
            
            # Check if we have images - return structured data for MCP processing
            if attached_images:
                return {
                    'text_content': user_text,
                    'attached_files': attached_files,
                    'attached_images': attached_images,
                    'continue_chat': continue_chat,
                    'language': language
                }
            
            # ====== TAG-BASED FORMAT - Clean and Simple ======
            # Start with clean user content
            full_response_text = user_text
            
            # Add attached files using collision-proof structured format
            if attached_files:
                full_response_text += "\n\n<AI_INTERACTION_ATTACHED_FILES>\n"
                workspace_name = None
                
                # Separate files and folders
                folders = []
                files = []
                errors = []
                
                for file_info in attached_files:
                    if "relative_path" in file_info:
                        relative_path = file_info.get('relative_path', 'unknown_path')
                        item_type = file_info.get('type', 'unknown')
                        workspace_name = file_info.get('workspace_name', '')
                        
                        if item_type.lower() == 'folder':
                            folders.append(relative_path)
                        elif item_type.lower() == 'file':
                            files.append(relative_path)
                    elif "error" in file_info:
                        error_name = file_info.get('name', 'unknown')
                        error_msg = file_info.get('error', 'Unknown error')
                        errors.append(f"{error_name} - {error_msg}")
                
                # Output structured sections
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
                
                if errors:
                    full_response_text += "ERRORS:\n"
                    for error in errors:
                        full_response_text += f"- {error}\n"
                    full_response_text += "\n"
                
                full_response_text += "</AI_INTERACTION_ATTACHED_FILES>\n"
                
                # Add workspace info
                if workspace_name:
                    full_response_text += f"\n<AI_INTERACTION_WORKSPACE>{workspace_name}</AI_INTERACTION_WORKSPACE>"
            
            # Add control tags at the end
            full_response_text += f"\n\n<AI_INTERACTION_CONTINUE_CHAT>{str(continue_chat).lower()}</AI_INTERACTION_CONTINUE_CHAT>"
            return full_response_text
            
        except json.JSONDecodeError:
            # Handle non-JSON case with clean tag format
            result_text = text
            result_text += f"\n\n<AI_INTERACTION_CONTINUE_CHAT>{str(continue_chat).lower()}</AI_INTERACTION_CONTINUE_CHAT>"
            return result_text
    else:
        # Empty case with clean tag format
        return """
<AI_INTERACTION_CONTINUE_CHAT>false</AI_INTERACTION_CONTINUE_CHAT>"""