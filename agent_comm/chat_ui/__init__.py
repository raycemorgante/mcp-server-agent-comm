# AI Interaction Tool Package
# Refactored for better maintainability and organization

from .core.dialog import InputDialog
from .core.config import ConfigManager
from .ui.file_dialog import FileAttachDialog
from .ui.file_tree import FileTreeView, FileSystemModel, FileTreeDelegate
from .ui.styles import get_main_stylesheet, get_file_dialog_stylesheet
from .utils.translations import get_translations, get_translation
from .utils.file_utils import read_file_content, validate_file_path

# Legacy compatibility - main entry point
from .engine import run_ui

# Import description
from .description import AI_INTERACTION_DESCRIPTION

__version__ = "2.2.0"
__author__ = "DemonVN"
__all__ = [
    # Core components
    'InputDialog',
    'ConfigManager',
    
    # UI components
    'FileAttachDialog',
    'FileTreeView',
    'FileSystemModel', 
    'FileTreeDelegate',
    'get_main_stylesheet',
    'get_file_dialog_stylesheet',
    
    # Utilities
    'get_translations',
    'get_translation',
    'read_file_content',
    'validate_file_path',
    
    # Main entry point
    'run_ui',
    
    # Description
    'AI_INTERACTION_DESCRIPTION'
]

def ai_interaction():
    return run_ui()