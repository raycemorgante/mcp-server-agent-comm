# File utilities for AI Interaction Tool
import os
import sys
import unicodedata
import re
import stat
import time
from pathlib import Path
from ..constants import SUPPORTED_ENCODINGS

# Try to import size limits, but use None if not defined (no limits)
try:
    from ..constants import MAX_FILE_SIZE_MB, MAX_ATTACHMENT_SIZE_MB
except ImportError:
    MAX_FILE_SIZE_MB = None
    MAX_ATTACHMENT_SIZE_MB = None

def normalize_path_unicode(path):
    """Chuẩn hóa path với Unicode normalization"""
    if not path:
        return ""
    
    try:
        normalized = unicodedata.normalize('NFC', str(path))
        cleaned = ''.join(char for char in normalized if ord(char) >= 32 or char in '\t\n\r')
        return cleaned
    except Exception:
        return str(path)

def validate_workspace_path(workspace_path):
    """Validate workspace path"""
    if not workspace_path:
        return {"valid": False, "error": "Workspace path is empty"}
    
    try:
        normalized_path = normalize_path_unicode(workspace_path)
        
        if not os.path.exists(normalized_path):
            return {"valid": False, "error": f"Workspace path does not exist: {normalized_path}"}
        
        if not os.path.isdir(normalized_path):
            return {"valid": False, "error": f"Workspace path is not a directory: {normalized_path}"}
        
        if not os.access(normalized_path, os.R_OK):
            return {"valid": False, "error": f"Cannot read workspace directory: {normalized_path}"}
        
        try:
            list(os.listdir(normalized_path)[:1])
        except PermissionError:
            return {"valid": False, "error": f"Permission denied for workspace: {normalized_path}"}
        except OSError as e:
            return {"valid": False, "error": f"Cannot access workspace: {str(e)}"}
        
        return {"valid": True, "normalized_path": normalized_path}
        
    except Exception as e:
        return {"valid": False, "error": f"Workspace validation error: {str(e)}"}

def validate_file_path_in_workspace(file_path, workspace_path):
    """Validate file path trong workspace"""
    if not file_path or not workspace_path:
        return {"valid": False, "error": "File path or workspace path is empty"}
    
    try:
        normalized_file = normalize_path_unicode(file_path)
        normalized_workspace = normalize_path_unicode(workspace_path)
        
        abs_file = os.path.abspath(normalized_file)
        abs_workspace = os.path.abspath(normalized_workspace)
        
        if not os.path.exists(abs_file):
            return {"valid": False, "error": f"File/folder does not exist: {normalized_file}"}
        
        if not os.access(abs_file, os.R_OK):
            return {"valid": False, "error": f"Cannot read file/folder: {normalized_file}"}
        
        try:
            relative_path = os.path.relpath(abs_file, abs_workspace)
            relative_path = relative_path.replace(os.sep, '/')
        except ValueError:
            return {"valid": False, "error": f"Cannot calculate relative path"}
        
        is_file = os.path.isfile(abs_file)
        is_dir = os.path.isdir(abs_file)
        is_symlink = os.path.islink(abs_file)
        
        return {
            "valid": True,
            "normalized_path": abs_file,
            "relative_path": relative_path,
            "is_file": is_file,
            "is_dir": is_dir,
            "is_symlink": is_symlink,
            "basename": os.path.basename(abs_file)
        }
        
    except Exception as e:
        return {"valid": False, "error": f"File validation error: {str(e)}"}

def create_relative_path_with_workspace(file_path, workspace_path):
    """Tạo relative path với workspace name"""
    try:
        validation = validate_file_path_in_workspace(file_path, workspace_path)
        if not validation["valid"]:
            return None, validation["error"]
        
        relative_path = validation["relative_path"]
        workspace_name = os.path.basename(os.path.normpath(workspace_path))
        full_relative_path = f"{workspace_name}/{relative_path}"
        
        return full_relative_path, None
        
    except Exception as e:
        return None, f"Error creating relative path: {str(e)}"

def read_file_content(file_path):
    """Đọc nội dung file với encoding detection"""        
    try:
        normalized_path = normalize_path_unicode(file_path)
        
        if not os.path.isfile(normalized_path):
            return {"success": False, "error": f"Path is not a file: {normalized_path}"}
        
        if not os.access(normalized_path, os.R_OK):
            return {"success": False, "error": f"Cannot read file: {normalized_path}"}
        
        try:
            file_size = os.path.getsize(normalized_path)
        except OSError as e:
            return {"success": False, "error": f"Cannot get file size: {str(e)}"}
        
        encodings = ['utf-8', 'utf-8-sig', 'utf-16', 'utf-16le', 'utf-16be', 
                    'latin-1', 'cp1252', 'gb2312', 'gbk', 'shift_jis', 'euc-kr']
        
        for encoding in encodings:
            try:
                with open(normalized_path, 'r', encoding=encoding, errors='replace') as file:
                    content = file.read()
                    
                replacement_ratio = content.count('\ufffd') / max(len(content), 1)
                if replacement_ratio < 0.1:
                    return {
                        "success": True,
                        "content": content,
                        "encoding": encoding,
                        "size": file_size,
                        "lines": content.count('\n') + 1
                    }
            except Exception:
                continue
        
        # Nếu không đọc được text, return thông tin basic
        return {
            "success": True,
            "content": f"[Binary/Unreadable file: {os.path.basename(normalized_path)}]",
            "encoding": "binary",
            "size": file_size,
            "lines": 0,
            "is_binary": True
        }
        
    except Exception as e:
        return {"success": False, "error": f"Error reading file: {str(e)}"}

def get_file_info_comprehensive(file_path):
    """Lấy thông tin file toàn diện"""
    try:
        normalized_path = normalize_path_unicode(file_path)
        stat_info = os.stat(normalized_path)
        
        is_file = os.path.isfile(normalized_path)
        is_dir = os.path.isdir(normalized_path)
        is_symlink = os.path.islink(normalized_path)
        
        permissions = {
            "readable": os.access(normalized_path, os.R_OK),
            "writable": os.access(normalized_path, os.W_OK),
            "executable": os.access(normalized_path, os.X_OK)
        }
        
        extension = ""
        if is_file:
            _, ext = os.path.splitext(normalized_path)
            extension = ext.lower()
        
        size_info = {"bytes": stat_info.st_size}
        if stat_info.st_size >= 1024**3:
            size_info["human"] = f"{stat_info.st_size / (1024**3):.1f} GB"
        elif stat_info.st_size >= 1024**2:
            size_info["human"] = f"{stat_info.st_size / (1024**2):.1f} MB" 
        elif stat_info.st_size >= 1024:
            size_info["human"] = f"{stat_info.st_size / 1024:.1f} KB"
        else:
            size_info["human"] = f"{stat_info.st_size} bytes"
        
        return {
            "success": True,
            "path": normalized_path,
            "basename": os.path.basename(normalized_path),
            "dirname": os.path.dirname(normalized_path),
            "extension": extension,
            "size": size_info,
            "is_file": is_file,
            "is_dir": is_dir,
            "is_symlink": is_symlink,
            "permissions": permissions,
            "modified_time": stat_info.st_mtime,
            "created_time": stat_info.st_ctime,
            "is_hidden": os.path.basename(normalized_path).startswith('.'),
        }
        
    except Exception as e:
        return {"success": False, "error": str(e), "path": file_path}

# Backward compatibility functions
def validate_file_path(file_path):
    try:
        normalized_path = normalize_path_unicode(file_path)
        
        if not os.path.exists(normalized_path):
            return {"valid": False, "error": f"Path does not exist: {normalized_path}"}
        
        if not os.access(normalized_path, os.R_OK):
            return {"valid": False, "error": f"Path is not readable: {normalized_path}"}
        
        return {"valid": True, "normalized_path": normalized_path}
        
    except Exception as e:
        return {"valid": False, "error": f"Path validation error: {str(e)}"}

def get_file_info_safe(file_path):
    return get_file_info_comprehensive(file_path)

def get_file_info(file_path):
    try:
        stat = os.stat(file_path)
        return {
            "name": os.path.basename(file_path),
            "path": file_path,
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "readable": os.access(file_path, os.R_OK),
            "writable": os.access(file_path, os.W_OK),
            "success": True
        }
    except Exception as e:
        return {"error": str(e), "success": False}