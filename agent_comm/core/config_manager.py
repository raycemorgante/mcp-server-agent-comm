"""
Config Manager - Handles UI configuration persistence
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from ..constants import CONFIG_FILE, UI_WIDTH, UI_HEIGHT


class ConfigManager:
    """Manages configuration persistence for UI settings"""
    
    def __init__(self):
        self.config_file = CONFIG_FILE
        self.default_config = {
            "window": {
                "width": UI_WIDTH,
                "height": UI_HEIGHT,
                "x": 100,
                "y": 100
            },
            "ui": {
                "splitter_sizes": [480, 420, 350],  # Default 3-column layout - generous Message Queue
                "auto_refresh_interval": 500
            }
        }
        
        # Ensure config file exists
        self._ensure_config_exists()
    
    def _ensure_config_exists(self):
        """Create default config if it doesn't exist"""
        if not self.config_file.exists():
            self.save_config(self.default_config)
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # Merge with defaults to ensure all keys exist
            return self._merge_with_defaults(config)
            
        except (FileNotFoundError, json.JSONDecodeError):
            # Return defaults if file missing or corrupted
            return self.default_config.copy()
    
    def save_config(self, config: Dict[str, Any]):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save config: {e}")
    
    def _merge_with_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge loaded config with defaults to ensure all keys exist"""
        merged = self.default_config.copy()
        
        # Recursively merge dictionaries
        for key, value in config.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key].update(value)
            else:
                merged[key] = value
        
        return merged
    
    def get_window_geometry(self) -> Dict[str, int]:
        """Get window geometry settings"""
        config = self.load_config()
        return config["window"]
    
    def save_window_geometry(self, width: int, height: int, x: int, y: int):
        """Save window geometry settings"""
        config = self.load_config()
        config["window"] = {
            "width": width,
            "height": height,
            "x": x,
            "y": y
        }
        self.save_config(config)
    
    def get_splitter_sizes(self) -> list:
        """Get splitter sizes"""
        config = self.load_config()
        return config["ui"]["splitter_sizes"]
    
    def save_splitter_sizes(self, sizes: list):
        """Save splitter sizes"""
        config = self.load_config()
        config["ui"]["splitter_sizes"] = sizes
        self.save_config(config)
    
    def get_refresh_interval(self) -> int:
        """Get auto refresh interval"""
        config = self.load_config()
        return config["ui"]["auto_refresh_interval"] 