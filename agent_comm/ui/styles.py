"""
Dark Theme Styles for Agent Communication Controller
Beautiful, modern dark UI with consistent color palette
"""

# Color Palette - Balanced Dark Theme
COLORS = {
    # Main Background Colors
    "bg_primary": "#2b2b2b",        # Main dark background (lighter)
    "bg_secondary": "#3c3c3c",      # Panel backgrounds (lighter)  
    "bg_tertiary": "#4a4a4a",       # Input/widget backgrounds (lighter)
    "bg_hover": "#505050",          # Hover states (lighter)
    
    # Text Colors
    "text_primary": "#ffffff",      # Main text
    "text_secondary": "#d0d0d0",    # Secondary text (lighter)
    "text_disabled": "#888888",     # Disabled text (lighter)
    "text_accent": "#5dade2",       # Accent text (headers) - more vibrant blue
    
    # Border Colors
    "border_primary": "#404040",    # Main borders
    "border_secondary": "#333333",  # Subtle borders
    "border_accent": "#64b5f6",     # Accent borders
    
    # Status Colors
    "success": "#4caf50",           # Green - success
    "warning": "#ff9800",           # Orange - warnings  
    "error": "#f44336",             # Red - errors
    "info": "#2196f3",              # Blue - info
    
    # Agent Colors
    "agent_1": "#e91e63",           # Pink for Agent 1
    "agent_2": "#00acc1",           # Cyan for Agent 2
    
    # Button Colors
    "btn_primary": "#1976d2",       # Primary action
    "btn_secondary": "#424242",     # Secondary action
    "btn_success": "#388e3c",       # Success action
    "btn_warning": "#f57c00",       # Warning action
    "btn_danger": "#d32f2f",        # Danger action
}

class Styles:
    """Modern Dark Theme Styles"""
    
    @staticmethod
    def get_main_window_style():
        """Main window styling with dialog text fix"""
        return f"""
        QDialog {{
            background-color: {COLORS['bg_primary']};
            color: {COLORS['text_primary']};
            font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
            font-size: 13px;
        }}
        
        /* Fix dialog text colors */
        QMessageBox {{
            background-color: {COLORS['bg_secondary']};
            color: {COLORS['text_primary']};
        }}
        QMessageBox QLabel {{
            color: {COLORS['text_primary']};
            background-color: transparent;
        }}
        QMessageBox QPushButton {{
            background-color: {COLORS['btn_primary']};
            color: white;
            border: none;
            border-radius: 4px;
            padding: 6px 12px;
            font-size: 11px;
        }}
        QMessageBox QPushButton:hover {{
            background-color: {COLORS['info']};
        }}
        """
    
    @staticmethod
    def get_header_style():
        """Header label styling - elegant and space-efficient"""
        return f"""
        QLabel {{
            background-color: transparent;
            color: #ffffff;
            font-weight: bold;
            font-size: 18px;
            margin: 0px;
            padding: 0px;
            border: none;
            text-align: center;
        }}
        """
    
    @staticmethod
    def get_group_box_style():
        """Group box styling for panels without title"""
        return f"""
        QGroupBox {{
            font-weight: bold;
            color: {COLORS['text_primary']};
            background-color: {COLORS['bg_secondary']};
            border: 2px solid {COLORS['border_primary']};
            border-radius: 8px;
            margin-top: 8px;
            padding: 8px;
        }}
        """
    
    @staticmethod
    def get_column_header_style():
        """Custom column header styling"""
        return f"""
        QLabel {{
            color: {COLORS['text_accent']};
            font-size: 14px;
            font-weight: bold;
            padding: 8px 12px 2px 12px;
            margin: 4px 0px 0px 0px;
            background-color: transparent;
            border: none;
        }}
        """
    
    @staticmethod
    def get_list_widget_style():
        """List widget styling with uniform item height"""
        return f"""
        QListWidget {{
            background-color: {COLORS['bg_tertiary']};
            border: 1px solid {COLORS['border_secondary']};
            border-radius: 6px;
            padding: 4px;
            color: {COLORS['text_primary']};
            selection-background-color: {COLORS['btn_primary']};
            outline: none;
        }}
        QListWidget::item {{
            padding: 6px 8px;
            margin: 1px;
            border-radius: 4px;
            border: none;
            min-height: 24px;
            max-height: 28px;
            height: 28px;
            width: 100%;
            max-width: 100%;
            white-space: nowrap;
        }}
        QListWidget::item:hover {{
            background-color: {COLORS['bg_hover']};
        }}
        QListWidget::item:selected {{
            background-color: {COLORS['btn_primary']};
            color: white;
        }}
        QListWidget::item:disabled {{
            color: {COLORS['text_disabled']};
            background-color: transparent;
        }}
        """
    
    @staticmethod
    def get_text_edit_style():
        """Text edit styling for message details"""
        return f"""
        QTextEdit {{
            background-color: {COLORS['bg_tertiary']};
            border: 1px solid {COLORS['border_secondary']};
            border-radius: 6px;
            padding: 8px;
            color: {COLORS['text_primary']};
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 12px;
            line-height: 1.4;
        }}
        QTextEdit:focus {{
            border: 2px solid {COLORS['border_accent']};
        }}
        """
    
    @staticmethod
    def get_button_style(button_type="primary"):
        """Button styling with different types"""
        color_map = {
            "primary": COLORS['btn_primary'],
            "secondary": COLORS['btn_secondary'], 
            "success": COLORS['btn_success'],
            "warning": COLORS['btn_warning'],
            "danger": COLORS['btn_danger'],
            "agent_1": COLORS['agent_1'],
            "agent_2": COLORS['agent_2'],
        }
        
        bg_color = color_map.get(button_type, COLORS['btn_primary'])
        hover_color = Styles._darken_color(bg_color, 0.2)
        
        return f"""
        QPushButton {{
            background-color: {bg_color};
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px 16px;
            font-size: 12px;
            font-weight: 500;
            min-height: 16px;
        }}
        QPushButton:hover {{
            background-color: {hover_color};
            border: 1px solid {COLORS['border_accent']};
        }}
        QPushButton:pressed {{
            background-color: {Styles._darken_color(bg_color, 0.3)};
            border: 1px solid {COLORS['border_primary']};
        }}
        QPushButton:disabled {{
            background-color: {COLORS['btn_secondary']};
            color: {COLORS['text_disabled']};
            border: none;
        }}
        """
    
    @staticmethod
    def get_status_label_style():
        """Status bar styling - compact version"""
        return f"""
        QLabel {{
            background-color: {COLORS['bg_secondary']};
            color: {COLORS['text_secondary']};
            border-top: 2px solid {COLORS['border_primary']};
            padding: 4px 8px;
            font-size: 10px;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            max-height: 24px;
            min-height: 24px;
        }}
        """
    
    @staticmethod
    def get_splitter_style():
        """Splitter styling"""
        return f"""
        QSplitter::handle {{
            background-color: {COLORS['border_primary']};
            width: 3px;
            height: 3px;
        }}
        QSplitter::handle:hover {{
            background-color: {COLORS['border_accent']};
        }}
        """
    
    @staticmethod
    def get_instruction_label_style():
        """Instruction label styling"""
        return f"""
        QLabel {{
            color: {COLORS['text_secondary']};
            font-size: 11px;
            padding: 4px 8px;
            background-color: transparent;
            font-style: italic;
        }}
        """
    
    # Status-specific styles
    @staticmethod
    def get_status_style(status_type="info"):
        """Dynamic status styling - compact version"""
        color_map = {
            "success": COLORS['success'],
            "warning": COLORS['warning'],
            "error": COLORS['error'],
            "info": COLORS['info'],
        }
        
        color = color_map.get(status_type, COLORS['info'])
        
        return f"""
        QLabel {{
            background-color: {COLORS['bg_secondary']};
            color: {color};
            border-top: 2px solid {COLORS['border_primary']};
            padding: 4px 8px;
            font-size: 10px;
            font-weight: bold;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            max-height: 24px;
            min-height: 24px;
        }}
        """
    
    # Utility methods
    @staticmethod
    def _darken_color(hex_color, factor):
        """Darken a hex color by a factor (0-1)"""
        # Remove # if present
        hex_color = hex_color.lstrip('#')
        
        # Convert to RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        # Darken
        r = int(r * (1 - factor))
        g = int(g * (1 - factor))
        b = int(b * (1 - factor))
        
        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}"


# Preset style combinations
STYLE_PRESETS = {
    "message_queue_panel": {
        "group_box": Styles.get_group_box_style(),
        "list_widget": Styles.get_list_widget_style(),
        "instruction_label": Styles.get_instruction_label_style(),
        "delete_btn": Styles.get_button_style("danger"),
        "select_btn": Styles.get_button_style("info"),
        "clear_btn": Styles.get_button_style("secondary"),
    },
    
    "waiting_agents_panel": {
        "group_box": Styles.get_group_box_style(),
        "list_widget": Styles.get_list_widget_style(), 
        "instruction_label": Styles.get_instruction_label_style(),
        "smart_delivery_btn": Styles.get_button_style("success"),
    },
    
    "message_details_panel": {
        "group_box": Styles.get_group_box_style(),
        "text_edit": Styles.get_text_edit_style(),
        "instruction_label": Styles.get_instruction_label_style(),
        "agent_1_btn": Styles.get_button_style("agent_1"),
        "agent_2_btn": Styles.get_button_style("agent_2"),
    },
    
    "control_buttons": {
        "refresh_btn": Styles.get_button_style("success"),
        "clear_all_btn": Styles.get_button_style("danger"),
    }
} 