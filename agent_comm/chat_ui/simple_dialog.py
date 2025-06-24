"""
Simplified AI Chat Dialog for agent communication
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, 
    QPushButton, QLabel, QApplication, QMessageBox,
    QCheckBox, QFrame, QSplitter
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

class SimpleAIChatDialog(QDialog):
    """Simplified AI Chat dialog for communicating with agents"""
    
    message_sent = pyqtSignal(str, bool)  # message, continue_chat
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.result_text = None
        self.result_continue = False
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the chat dialog UI"""
        self.setWindowTitle("💬 AI Chat - Communicate with Both Agents")
        self.setMinimumSize(800, 600)
        self.resize(1000, 700)
        
        # Apply dark theme similar to controller
        self.setStyleSheet("""
        QDialog {
            background-color: #2b2b2b;
            color: #ffffff;
            font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
        }
        QLabel {
            color: #ffffff;
        }
        QTextEdit {
            background-color: #3c3c3c;
            border: 1px solid #555555;
            border-radius: 6px;
            padding: 8px;
            color: #ffffff;
            font-size: 12px;
        }
        QPushButton {
            background-color: #4a9eff;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px 16px;
            font-size: 12px;
            font-weight: 500;
        }
        QPushButton:hover {
            background-color: #3a8eef;
        }
        QPushButton:pressed {
            background-color: #2a7edf;
        }
        QPushButton:disabled {
            background-color: #666666;
            color: #999999;
        }
        QCheckBox {
            color: #ffffff;
            spacing: 8px;
        }
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
        }
        QCheckBox::indicator:unchecked {
            background-color: #3c3c3c;
            border: 1px solid #555555;
            border-radius: 3px;
        }
        QCheckBox::indicator:checked {
            background-color: #4a9eff;
            border: 1px solid #4a9eff;
            border-radius: 3px;
        }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_label = QLabel("💬 AI Chat - Communicate with Both Agents")
        header_label.setAlignment(Qt.AlignCenter)
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header_label.setFont(header_font)
        layout.addWidget(header_label)
        
        # Info
        info_label = QLabel(
            "🤖 Send messages to communicate with both Agent 1 and Agent 2 simultaneously.\n"
            "Your message will be delivered to both agents through the agent communication system."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #cccccc; font-size: 11px; padding: 8px; background-color: #3c3c3c; border-radius: 6px;")
        layout.addWidget(info_label)
        
        # Message input area
        input_label = QLabel("💭 Your Message:")
        input_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(input_label)
        
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText(
            "Type your message here...\n\n"
            "Example: 'Hello both agents! Can you help me with...'"
        )
        self.message_input.setMaximumHeight(200)
        layout.addWidget(self.message_input)
        
        # Options
        options_frame = QFrame()
        options_layout = QHBoxLayout(options_frame)
        
        self.continue_chat_cb = QCheckBox("Continue conversation (keep chat window open)")
        self.continue_chat_cb.setChecked(True)
        options_layout.addWidget(self.continue_chat_cb)
        
        options_layout.addStretch()
        layout.addWidget(options_frame)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.send_btn = QPushButton("📤 Send to Both Agents")
        self.send_btn.clicked.connect(self.send_message)
        self.send_btn.setStyleSheet("""
        QPushButton {
            background-color: #28a745;
            font-size: 13px;
            font-weight: bold;
            padding: 12px 20px;
        }
        QPushButton:hover {
            background-color: #218838;
        }
        """)
        
        self.cancel_btn = QPushButton("❌ Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setStyleSheet("""
        QPushButton {
            background-color: #dc3545;
            font-size: 13px;
            padding: 12px 20px;
        }
        QPushButton:hover {
            background-color: #c82333;
        }
        """)
        
        button_layout.addStretch()
        button_layout.addWidget(self.send_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        
        # Focus on input
        self.message_input.setFocus()
        
    def send_message(self):
        """Send message to both agents"""
        message = self.message_input.toPlainText().strip()
        
        if not message:
            QMessageBox.warning(self, "Empty Message", "Please enter a message before sending.")
            return
            
        # Store results
        self.result_text = message
        self.result_continue = self.continue_chat_cb.isChecked()
        
        # Emit signal
        self.message_sent.emit(message, self.result_continue)
        
        # Accept dialog
        self.accept()
    
    def get_result(self):
        """Get the message and continue flag"""
        return self.result_text, self.result_continue


def show_simple_ai_chat_dialog(parent=None):
    """Show simplified AI chat dialog"""
    dialog = SimpleAIChatDialog(parent)
    
    if dialog.exec_() == QDialog.Accepted:
        return dialog.get_result()
    
    return None, False


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    
    result = show_simple_ai_chat_dialog()
    print(f"Result: {result}")
    
    sys.exit() 