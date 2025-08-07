"""
Controller UI - Main interface for controlling message flow between agents
"""

import sys
from typing import Optional, Dict, Any, List
from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QLabel, QListWidget, QListWidgetItem,
    QMessageBox, QGroupBox, QSplitter, QFrame, QWidget
)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QFont

from ..core.flow_manager import FlowManager
from ..core.config_manager import ConfigManager
from .styles import Styles, STYLE_PRESETS


class ControllerUI(QDialog):
    """Main controller UI for agent communication flow"""
    
    def __init__(self):
        super().__init__()
        
        self.flow_manager = FlowManager()
        self.config_manager = ConfigManager()
        self.result = None
        
        self.conversations_widget = None
        self.message_queue_widget = None
        self.detail_display = None
        self.current_conversations = {}
        
        self.init_ui()
        self.setup_timer()
        self.refresh_data()
    
    def init_ui(self):
        """Initialize the controller UI"""
        self.setWindowTitle("🎮 Agent Communication Controller")
        
        # Apply main window dark theme
        self.setStyleSheet(Styles.get_main_window_style())
        
        # Load saved window geometry
        geometry = self.config_manager.get_window_geometry()
        self.setGeometry(geometry["x"], geometry["y"], geometry["width"], geometry["height"])
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)  # Slightly larger margins for dark theme
        layout.setSpacing(8)  # Better spacing for dark theme
        
        # Beautiful header with dark theme - space-efficient
        header_label = QLabel("🎮 Agent Communication Controller")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet(Styles.get_header_style())
        # Set compact height: font(18px) minimal padding = 32px
        header_label.setFixedHeight(32)
        layout.addWidget(header_label)
        
        # Main content splitter - 3 columns layout
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Column 1 - Message Queue
        message_queue_panel = self._create_message_queue_panel()
        splitter.addWidget(message_queue_panel)
        
        # Column 2 - Conversations
        agents_panel = self._create_conversations_panel()
        splitter.addWidget(agents_panel)
        
        # Column 3 - Message Details
        details_panel = self._create_message_details_panel()
        splitter.addWidget(details_panel)
        
        # Apply beautiful splitter styling
        splitter.setStyleSheet(Styles.get_splitter_style())
        
        # Set splitter proportions from config (3 columns now)
        saved_sizes = self.config_manager.get_splitter_sizes()
        if len(saved_sizes) == 3:
            splitter.setSizes(saved_sizes)
        else:
            # Default 3-column layout: generous Message Queue space
            splitter.setSizes([480, 420, 350])
        
        # Set minimum widths for better UX
        splitter.setChildrenCollapsible(False)  # Prevent collapse
        if splitter.count() >= 3:
            # Message Queue: min 480px (generous space for 3 buttons with full text)
            message_queue_panel.setMinimumWidth(480)
            # Waiting Agents: min 400px (wider for better readability)  
            agents_panel.setMinimumWidth(400)
            # Message Details: min 350px
            details_panel.setMinimumWidth(350)
        
        # Save splitter sizes when changed
        self.main_splitter = splitter
        splitter.splitterMoved.connect(self._on_splitter_moved)
        
        # Beautiful control buttons with dark theme
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)  # More spacing for better look
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.refresh_data)
        self.refresh_btn.setStyleSheet(STYLE_PRESETS["control_buttons"]["refresh_btn"])
        button_layout.addWidget(self.refresh_btn)
        
        self.clear_all_btn = QPushButton("🗑️ Clear All Data")
        self.clear_all_btn.clicked.connect(self.clear_all_data)
        self.clear_all_btn.setStyleSheet(STYLE_PRESETS["control_buttons"]["clear_all_btn"])
        button_layout.addWidget(self.clear_all_btn)
        
        # Add AI Chat button
        self.ai_chat_btn = QPushButton("💬 AI Chat")
        self.ai_chat_btn.clicked.connect(self.open_ai_chat)
        self.ai_chat_btn.setStyleSheet(STYLE_PRESETS["control_buttons"]["refresh_btn"])  # Use same style as refresh
        button_layout.addWidget(self.ai_chat_btn)
        
        layout.addLayout(button_layout)
        
        # Beautiful status bar with dark theme
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet(Styles.get_status_label_style())
        layout.addWidget(self.status_label)
    
    def _create_message_queue_panel(self) -> QWidget:
        """Create standalone message queue panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        # Custom header
        header_label = QLabel("Message Queue")
        header_label.setStyleSheet(Styles.get_column_header_style())
        layout.addWidget(header_label)
        
        # Content group box
        content_group = QGroupBox()
        content_group.setStyleSheet(STYLE_PRESETS["message_queue_panel"]["group_box"])
        content_layout = QVBoxLayout(content_group)
        content_layout.setContentsMargins(8, 4, 8, 8)
        
        # Instructions with beautiful styling
        info_label = QLabel("Messages waiting to be delivered:")
        info_label.setStyleSheet(STYLE_PRESETS["message_queue_panel"]["instruction_label"])
        content_layout.addWidget(info_label)
        
        # Message queue list with dark theme
        self.message_queue_widget = QListWidget()
        self.message_queue_widget.setSelectionMode(QListWidget.ExtendedSelection)  # Enable multi-select
        self.message_queue_widget.itemClicked.connect(self._on_message_selected)
        self.message_queue_widget.setStyleSheet(STYLE_PRESETS["message_queue_panel"]["list_widget"])
        content_layout.addWidget(self.message_queue_widget)
        
        # Beautiful message queue actions
        queue_actions_layout = QHBoxLayout()
        queue_actions_layout.setSpacing(8)
        
        self.delete_selected_btn = QPushButton("🗑️ Delete Selected")
        self.delete_selected_btn.clicked.connect(self.delete_selected_messages)
        self.delete_selected_btn.setEnabled(False)
        self.delete_selected_btn.setStyleSheet(STYLE_PRESETS["message_queue_panel"]["delete_btn"])
        queue_actions_layout.addWidget(self.delete_selected_btn)
        
        self.select_all_btn = QPushButton("☑️ Select All")
        self.select_all_btn.clicked.connect(self.select_all_messages)
        self.select_all_btn.setStyleSheet(STYLE_PRESETS["message_queue_panel"]["select_btn"])
        queue_actions_layout.addWidget(self.select_all_btn)
        
        self.clear_selection_btn = QPushButton("❌ Clear Selection")
        self.clear_selection_btn.clicked.connect(self.clear_message_selection)
        self.clear_selection_btn.setStyleSheet(STYLE_PRESETS["message_queue_panel"]["clear_btn"])
        queue_actions_layout.addWidget(self.clear_selection_btn)
        
        content_layout.addLayout(queue_actions_layout)
        
        layout.addWidget(content_group)
        
        return panel
    
    def _create_conversations_panel(self) -> QWidget:
        """Create conversations panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        header_label = QLabel("Conversations")
        header_label.setStyleSheet(Styles.get_column_header_style())
        layout.addWidget(header_label)

        content_group = QGroupBox()
        content_group.setStyleSheet(STYLE_PRESETS["waiting_agents_panel"]["group_box"])
        content_layout = QVBoxLayout(content_group)
        content_layout.setContentsMargins(8, 4, 8, 8)

        info_label = QLabel("Active conversations:")
        info_label.setStyleSheet(STYLE_PRESETS["waiting_agents_panel"]["instruction_label"])
        content_layout.addWidget(info_label)

        self.conversations_widget = QListWidget()
        self.conversations_widget.setStyleSheet(STYLE_PRESETS["waiting_agents_panel"]["list_widget"])
        content_layout.addWidget(self.conversations_widget)

        layout.addWidget(content_group)
        return panel
    
    def _create_message_details_panel(self) -> QWidget:
        """Create message details panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        # Custom header
        header_label = QLabel("Message Details")
        header_label.setStyleSheet(Styles.get_column_header_style())
        layout.addWidget(header_label)
        
        # Content group box
        content_group = QGroupBox()
        content_group.setStyleSheet(STYLE_PRESETS["message_details_panel"]["group_box"])
        content_layout = QVBoxLayout(content_group)
        content_layout.setContentsMargins(8, 4, 8, 8)
        
        # Instructions with beautiful styling
        info_label = QLabel("Message content and delivery options:")
        info_label.setStyleSheet(STYLE_PRESETS["message_details_panel"]["instruction_label"])
        content_layout.addWidget(info_label)
        
        # Message content display with dark theme
        self.detail_display = QTextEdit()
        self.detail_display.setReadOnly(True)
        self.detail_display.setPlainText("Select a message to view details")
        self.detail_display.setStyleSheet(STYLE_PRESETS["message_details_panel"]["text_edit"])
        content_layout.addWidget(self.detail_display)
        
        # Participants list
        self.participants_list = QListWidget()
        self.participants_list.setSelectionMode(QListWidget.MultiSelection)
        self.participants_list.itemSelectionChanged.connect(self._on_participant_selection)
        self.participants_list.setStyleSheet(STYLE_PRESETS["waiting_agents_panel"]["list_widget"])
        content_layout.addWidget(self.participants_list)

        # Delivery actions
        delivery_layout = QHBoxLayout()
        delivery_layout.setSpacing(8)

        self.deliver_to_1_btn = QPushButton("📡 Broadcast")
        self.deliver_to_1_btn.clicked.connect(self.broadcast_message)
        self.deliver_to_1_btn.setEnabled(False)
        self.deliver_to_1_btn.setStyleSheet(STYLE_PRESETS["message_details_panel"]["agent_1_btn"])
        delivery_layout.addWidget(self.deliver_to_1_btn)

        self.deliver_to_2_btn = QPushButton("🎯 Send Selected")
        self.deliver_to_2_btn.clicked.connect(self.send_selected_message)
        self.deliver_to_2_btn.setEnabled(False)
        self.deliver_to_2_btn.setStyleSheet(STYLE_PRESETS["message_details_panel"]["agent_2_btn"])
        delivery_layout.addWidget(self.deliver_to_2_btn)

        content_layout.addLayout(delivery_layout)
        
        layout.addWidget(content_group)
        
        return panel
    

    
    def refresh_data(self):
        """Refresh all data from flow manager"""
        try:
            data = self.flow_manager.get_controller_data()
            
            # Safely get data with defaults
            conversations = data.get("conversations", {})
            message_queue = data.get("message_queue", [])
            timestamp = data.get("timestamp", "")

            self.current_conversations = conversations or {}
            self._update_conversations(conversations)
            self._update_message_queue(message_queue)

            conv_count = len(conversations) if conversations else 0
            queue_count = len(message_queue) if message_queue else 0

            timestamp_display = timestamp[:19] if timestamp and len(timestamp) >= 19 else "Unknown"

            self.status_label.setText(f"📊 {conv_count} conversations • {queue_count} pending messages • Last update: {timestamp_display}")
            
        except Exception as e:
            # Handle errors gracefully without spam
            error_msg = f"Failed to refresh data: {str(e)}"
            
            # Update status to show error but don't show popup every 3 seconds
            self.status_label.setText(f"❌ Error: {error_msg}")
            
            # Clear UI widgets to prevent display of stale data
            if hasattr(self, 'conversations_widget') and self.conversations_widget:
                self.conversations_widget.clear()
                item = QListWidgetItem("Error loading conversations")
                item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
                self.conversations_widget.addItem(item)
                
            if hasattr(self, 'message_queue_widget') and self.message_queue_widget:
                self.message_queue_widget.clear()
                item = QListWidgetItem("Error loading message queue")
                item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
                self.message_queue_widget.addItem(item)
    
    def _update_conversations(self, conversations: Dict[str, Any]):
        """Update conversations list"""
        selected_ids = []
        for item in self.conversations_widget.selectedItems():
            conv_id = item.data(Qt.UserRole)
            if conv_id:
                selected_ids.append(conv_id)

        self.conversations_widget.clear()

        if not conversations:
            item = QListWidgetItem("No active conversations")
            item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
            self.conversations_widget.addItem(item)
            return

        try:
            sorted_convs = sorted(conversations.items(), key=lambda x: x[1].get("last_update", ""), reverse=True)
        except Exception:
            sorted_convs = conversations.items()

        for conv_id, conv_data in sorted_convs:
            participants = ", ".join(conv_data.get("participants", []))
            item = QListWidgetItem(f"{conv_id}: {participants}")
            item.setData(Qt.UserRole, conv_id)
            self.conversations_widget.addItem(item)

        if selected_ids:
            for i in range(self.conversations_widget.count()):
                item = self.conversations_widget.item(i)
                if item and item.data(Qt.UserRole) in selected_ids:
                    item.setSelected(True)

    def _update_message_queue(self, message_queue: List[Dict[str, Any]]):
        """Update message queue list"""
        # Store current scroll position and selection
        current_item_count = self.message_queue_widget.count()
        
        # Save current selection message IDs
        selected_message_ids = []
        for item in self.message_queue_widget.selectedItems():
            msg_data = item.data(Qt.UserRole)
            if msg_data and msg_data.get("id"):
                selected_message_ids.append(msg_data.get("id"))
        
        self.message_queue_widget.clear()
        
        # Handle empty or None message queue
        if not message_queue:
            item = QListWidgetItem("No messages in queue")
            item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
            self.message_queue_widget.addItem(item)
            self.delete_selected_btn.setEnabled(False)
            return
        
        # Sort messages by timestamp descending (newest first) for better UX
        try:
            sorted_messages = sorted(message_queue, 
                                   key=lambda x: x.get("timestamp", ""), 
                                   reverse=True)
        except:
            # Fallback if sorting fails
            sorted_messages = message_queue
        
        # Process each message safely (newest first order)
        for msg in sorted_messages:
            try:
                # Safely extract message data with defaults
                from_agent = msg.get("from_agent", "unknown") if msg else "unknown"
                delivered = msg.get("delivered_all", False) if msg else False
                timestamp = msg.get("timestamp", "") if msg else ""
                message_content = msg.get("message", "") if msg else ""
                
                # Safely format timestamp
                timestamp_display = timestamp[:19] if timestamp and len(timestamp) >= 19 else "Unknown"
                
                # ROBUST text extraction: handle all formats
                message_preview = ""
                
                # Check if JSON format (mixed JSON + AI_INTERACTION tags)
                if message_content.strip().startswith('{'):
                    try:
                        import json
                        json_part = message_content.split("<AI_INTERACTION_")[0].strip()
                        parsed = json.loads(json_part)
                        # Extract text from JSON
                        preview_text = (parsed.get('text_content') or 
                                      parsed.get('text') or 
                                      parsed.get('content', ''))
                        if preview_text and preview_text.strip():
                            message_preview = preview_text[:45]
                    except:
                        pass
                
                # Check if pure AI_INTERACTION format (text + tags)
                elif "<AI_INTERACTION_" in message_content:
                    # Extract text before first AI_INTERACTION tag
                    text_part = message_content.split("<AI_INTERACTION_")[0].strip()
                    if text_part:
                        message_preview = text_part[:45]
                
                # Fallback: regular text message
                if not message_preview:
                    # Avoid showing base64 or very long content
                    if 'base64' in message_content or len(message_content) > 1000:
                        message_preview = "Message with attachments"
                    else:
                        message_preview = message_content[:45]
                
                if len(message_preview) > 45:
                    message_preview = message_preview[:45] + "..."
                
                status_icon = "✅" if delivered else "⏳"
                conv_id = msg.get("conversation_id", "") if msg else ""
                display_text = f"{status_icon} [{conv_id}] From {from_agent}: {message_preview}"
                
                item = QListWidgetItem(display_text)
                item.setData(Qt.UserRole, msg)
                item.setBackground(Qt.lightGray if delivered else Qt.white)
                
                # Set fixed height for consistent appearance
                item.setSizeHint(QSize(-1, 28))  # Fixed height of 28px for more items
                
                # ROBUST tooltip text extraction (consistent with preview)
                tooltip_message = ""
                
                # Check if JSON format (mixed JSON + AI_INTERACTION tags)
                if message_content.strip().startswith('{'):
                    try:
                        import json
                        json_part = message_content.split("<AI_INTERACTION_")[0].strip()
                        parsed = json.loads(json_part)
                        # Extract text from JSON
                        tooltip_text = (parsed.get('text_content') or 
                                      parsed.get('text') or 
                                      parsed.get('content', ''))
                        if tooltip_text and tooltip_text.strip():
                            tooltip_message = tooltip_text
                    except:
                        pass
                
                # Check if pure AI_INTERACTION format (text + tags)
                elif "<AI_INTERACTION_" in message_content:
                    # Extract text before first AI_INTERACTION tag
                    text_part = message_content.split("<AI_INTERACTION_")[0].strip()
                    if text_part:
                        tooltip_message = text_part
                
                # Fallback: regular text message
                if not tooltip_message:
                    # Avoid showing base64 or very long content
                    if 'base64' in message_content or len(message_content) > 300:
                        tooltip_message = "Message with attachments (click to view details)"
                    else:
                        tooltip_message = message_content
                
                # Always apply length limit with "..." for consistency
                if len(tooltip_message) > 150:
                    tooltip_message = tooltip_message[:150] + "..."
                
                full_tooltip = f"From: {from_agent}\nTime: {timestamp_display}\nMessage: {tooltip_message}"
                item.setToolTip(full_tooltip)
                
                self.message_queue_widget.addItem(item)
                
            except Exception as e:
                # If there's an error processing a specific message, add error item
                error_item = QListWidgetItem(f"❌ Error processing message: {str(e)}")
                error_item.setFlags(error_item.flags() & ~Qt.ItemIsEnabled)
                self.message_queue_widget.addItem(error_item)
        
        # With newest-first sorting, keep current scroll position for better UX
        new_item_count = self.message_queue_widget.count()
        if new_item_count > current_item_count:
            # New messages appear at top, so scroll to top to show newest
            self.message_queue_widget.scrollToTop()
        
        # Restore selection
        if selected_message_ids:
            for i in range(self.message_queue_widget.count()):
                item = self.message_queue_widget.item(i)
                if item:
                    msg_data = item.data(Qt.UserRole)
                    if msg_data and msg_data.get("id") in selected_message_ids:
                        item.setSelected(True)
        
        # Update delete button state
        self._update_delete_button_state()
    
    
    def _format_message_content(self, message_content: str) -> str:
        """Format message content for better readability in UI"""
        import json
        import re
        
        if not message_content:
            return "Empty message"
        
        # Check for mixed format (JSON + AI_INTERACTION tags)
        if message_content.strip().startswith('{') and ("<AI_INTERACTION_CONTINUE_CHAT>" in message_content):
            return self._format_mixed_json_message(message_content)
        
        # Check if this is pure ai_interaction format (with tags only)
        if "<AI_INTERACTION_ATTACHED_FILES>" in message_content or "<AI_INTERACTION_CONTINUE_CHAT>" in message_content:
            return self._format_ai_interaction_message(message_content)
        
        # Try to parse as JSON first (for messages with images/files)
        if message_content.strip().startswith('{'):
            try:
                parsed = json.loads(message_content)
                
                # Extract key information for display
                formatted_parts = []
                
                # Text content
                text_content = parsed.get('text_content') or parsed.get('text', '')
                if text_content:
                    formatted_parts.append(f"📝 Text Content:\n{text_content}\n")
                
                # Attached files
                attached_files = parsed.get('attached_files', [])
                if attached_files:
                    files_info = []
                    folders_info = []
                    
                    for file_info in attached_files:
                        if isinstance(file_info, dict):
                            relative_path = file_info.get('relative_path', 'unknown')
                            file_type = file_info.get('type', 'unknown')
                            if file_type == 'file':
                                files_info.append(f"  📄 {relative_path}")
                            elif file_type == 'folder':
                                folders_info.append(f"  📁 {relative_path}")
                    
                    if folders_info:
                        formatted_parts.append("📁 Attached Folders:")
                        formatted_parts.extend(folders_info)
                        formatted_parts.append("")
                    
                    if files_info:
                        formatted_parts.append("📄 Attached Files:")
                        formatted_parts.extend(files_info)
                        formatted_parts.append("")
                
                # Attached images (show summary, not base64 data)
                attached_images = parsed.get('attached_images', [])
                if attached_images:
                    image_count = len(attached_images)
                    formatted_parts.append(f"🖼️ Attached Images: {image_count} image(s)")
                    
                    # Add image details without base64 data
                    for i, img in enumerate(attached_images, 1):
                        if isinstance(img, dict):
                            filename = img.get('filename', f'image_{i}.png')
                            # Try to determine type from filename or default
                            if '.' in filename:
                                ext = filename.split('.')[-1].lower()
                                img_type = f"image/{ext}"
                            else:
                                img_type = "image/png"
                            formatted_parts.append(f"  📷 Image {i}: {filename} ({img_type})")
                    formatted_parts.append("")
                
                # Workspace
                workspace_name = parsed.get('workspace_name', '')
                if workspace_name:
                    formatted_parts.append(f"📂 Workspace: {workspace_name}\n")
                
                # Continue chat flag
                if 'continue_chat' in parsed:
                    continue_status = "Yes" if parsed.get('continue_chat', False) else "No"
                    formatted_parts.append(f"🔄 Continue Chat: {continue_status}")
                
                # Default source for regular JSON messages (usually admin)
                source_icon = "👑"
                formatted_parts.append(f"{source_icon} Source: Admin")
                
                result = "\n".join(formatted_parts).strip()
                return result if result else "Empty message content"
                
            except (json.JSONDecodeError, KeyError, Exception) as e:
                # If JSON parsing fails, fall back to text processing
                pass
        
        # Fallback: clean up the raw text for better readability
        # Preserve line breaks but clean up excessive whitespace
        lines = message_content.strip().split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Clean each line but preserve line structure
            cleaned_line = re.sub(r'\s+', ' ', line.strip())
            if cleaned_line:  # Skip empty lines after cleaning
                cleaned_lines.append(cleaned_line)
        
        cleaned = '\n'.join(cleaned_lines)
        
        # If still too long, truncate with preview
        if len(cleaned) > 500:
            return cleaned[:500] + "\n\n... (truncated, full content available in raw format)"
        
        return cleaned
    
    def _format_ai_interaction_message(self, message_content: str) -> str:
        """Format ai_interaction style message content"""
        import re
        
        formatted_parts = []
        
        # Extract main text content (before tags)
        main_text = message_content.split("<AI_INTERACTION_ATTACHED_FILES>")[0].strip()
        if main_text:
            formatted_parts.append(f"📝 Text Content:\n{main_text}\n")
        
        # Extract attached files info
        if "<AI_INTERACTION_ATTACHED_FILES>" in message_content:
            files_section = re.search(
                r'<AI_INTERACTION_ATTACHED_FILES>(.*?)</AI_INTERACTION_ATTACHED_FILES>', 
                message_content, 
                re.DOTALL
            )
            
            if files_section:
                files_content = files_section.group(1).strip()
                
                # Parse folders
                folders_match = re.search(r'FOLDERS:\s*(.*?)(?=\nFILES:|$)', files_content, re.DOTALL)
                if folders_match:
                    folders_text = folders_match.group(1).strip()
                    if folders_text:
                        formatted_parts.append("📁 Attached Folders:")
                        for line in folders_text.split('\n'):
                            line = line.strip()
                            if line.startswith('- '):
                                formatted_parts.append(f"  📁 {line[2:]}")
                        formatted_parts.append("")
                
                # Parse files
                files_match = re.search(r'FILES:\s*(.*?)$', files_content, re.DOTALL)
                if files_match:
                    files_text = files_match.group(1).strip()
                    if files_text:
                        formatted_parts.append("📄 Attached Files:")
                        for line in files_text.split('\n'):
                            line = line.strip()
                            if line.startswith('- '):
                                formatted_parts.append(f"  📄 {line[2:]}")
                        formatted_parts.append("")
        
        # Extract workspace info
        workspace_match = re.search(r'<AI_INTERACTION_WORKSPACE>(.*?)</AI_INTERACTION_WORKSPACE>', message_content)
        if workspace_match:
            workspace = workspace_match.group(1).strip()
            formatted_parts.append(f"📂 Workspace: {workspace}\n")
        
        # Extract source info
        source_match = re.search(r'<AI_INTERACTION_SOURCE>(.*?)</AI_INTERACTION_SOURCE>', message_content)
        if source_match:
            source = source_match.group(1).strip()
            source_icon = "👑" if source == "admin" else "🤖"
            formatted_parts.append(f"{source_icon} Source: {source.title()}")
        
        # Extract continue chat flag
        continue_match = re.search(r'<AI_INTERACTION_CONTINUE_CHAT>(.*?)</AI_INTERACTION_CONTINUE_CHAT>', message_content)
        if continue_match:
            continue_flag = continue_match.group(1).strip()
            continue_status = "Yes" if continue_flag.lower() == "true" else "No"
            formatted_parts.append(f"🔄 Continue Chat: {continue_status}")
        
        return "".join(formatted_parts).strip() if formatted_parts else "Empty message"
    
    def _format_mixed_json_message(self, message_content: str) -> str:
        """Format mixed JSON + ai_interaction format message"""
        import json
        import re
        
        formatted_parts = []
        
        # Extract JSON part (before AI_INTERACTION tags)
        json_part = message_content.split("<AI_INTERACTION_CONTINUE_CHAT>")[0].strip()
        
        try:
            if json_part.startswith('{'):
                parsed = json.loads(json_part)
                
                # Text content
                text_content = parsed.get('text_content') or parsed.get('text', '')
                if text_content:
                    formatted_parts.append(f"📝 Text Content:\n{text_content}\n")
                
                # Attached files
                attached_files = parsed.get('attached_files', [])
                if attached_files:
                    files_info = []
                    folders_info = []
                    
                    for file_info in attached_files:
                        if isinstance(file_info, dict):
                            relative_path = file_info.get('relative_path', 'unknown')
                            file_type = file_info.get('type', 'unknown')
                            if file_type == 'file':
                                files_info.append(f"  📄 {relative_path}")
                            elif file_type == 'folder':
                                folders_info.append(f"  📁 {relative_path}")
                    
                    if folders_info:
                        formatted_parts.append("📁 Attached Folders:")
                        formatted_parts.extend(folders_info)
                        formatted_parts.append("")
                    
                    if files_info:
                        formatted_parts.append("📄 Attached Files:")
                        formatted_parts.extend(files_info)
                        formatted_parts.append("")
                
                # Attached images (show summary, not base64 data)
                attached_images = parsed.get('attached_images', [])
                if attached_images:
                    image_count = len(attached_images)
                    formatted_parts.append(f"🖼️ Attached Images: {image_count} image(s)")
                    
                    # Add image details without base64 data
                    for i, img in enumerate(attached_images, 1):
                        if isinstance(img, dict):
                            filename = img.get('filename', f'image_{i}.png')
                            media_type = img.get('media_type', 'image/png')
                            formatted_parts.append(f"  📷 Image {i}: {filename} ({media_type})")
                    formatted_parts.append("")
                
                # Workspace
                workspace_name = parsed.get('workspace_name', '')
                if workspace_name:
                    formatted_parts.append(f"📂 Workspace: {workspace_name}\n")
                
                # Continue chat flag from JSON
                if 'continue_chat' in parsed:
                    continue_status = "Yes" if parsed.get('continue_chat', False) else "No"
                    formatted_parts.append(f"🔄 Continue Chat: {continue_status}")
                
                # Language
                language = parsed.get('language', '')
                if language:
                    formatted_parts.append(f"🌐 Language: {language}")
                
                # Extract source from tags part (default to admin for JSON messages from controller)
                source = "admin"  # Default for mixed format messages
                if "<AI_INTERACTION_SOURCE>agent</AI_INTERACTION_SOURCE>" in message_content:
                    source = "agent"
                elif "<AI_INTERACTION_SOURCE>admin</AI_INTERACTION_SOURCE>" in message_content:
                    source = "admin"
                
                source_icon = "👑" if source == "admin" else "🤖"
                formatted_parts.append(f"{source_icon} Source: {source.title()}")
                
        except (json.JSONDecodeError, KeyError, Exception):
            # If JSON parsing fails, fall back to text processing
            formatted_parts.append(f"📝 Content:\n{json_part}")
        
        result = "\n".join(formatted_parts).strip()
        return result if result else "Empty message content"

    def _on_message_selected(self, item: QListWidgetItem):
        """Handle message selection"""
        selected_items = self.message_queue_widget.selectedItems()
        
        # Update delete button state
        self._update_delete_button_state()
        
        # Handle single selection for details display
        if len(selected_items) == 1:
            msg_data = selected_items[0].data(Qt.UserRole)
            if msg_data:
                self.selected_message = msg_data
                conv_id = msg_data.get("conversation_id")
                participants = self.current_conversations.get(conv_id, {}).get("participants", [])
                from_agent = msg_data.get("from_agent", "")
                self.participants_list.clear()
                for p in participants:
                    if p != from_agent:
                        self.participants_list.addItem(p)

                self.deliver_to_1_btn.setEnabled(len(participants) > 1)
                self.deliver_to_2_btn.setEnabled(False)
                
                # Smart hybrid approach: formatted for complex JSON, raw for simple text
                raw_message = msg_data.get("message", "")
                
                # Simple approach like waiting agent selection + basic image handling
                if (raw_message.strip().startswith('{') and 
                    ('base64' in raw_message or len(raw_message) > 1000)):
                    # Complex JSON with images - create simple summary
                    try:
                        import json
                        json_part = raw_message.split("<AI_INTERACTION_")[0].strip()
                        parsed = json.loads(json_part)
                        
                        # Extract basic info
                        text_content = parsed.get('text_content', parsed.get('text', ''))
                        attached_images = parsed.get('attached_images', [])
                        attached_files = parsed.get('attached_files', [])
                        
                        # Create detailed summary with specific files/folders
                        summary_parts = []
                        if text_content:
                            summary_parts.append(f"📝 Text: {text_content}")
                        
                        if attached_images:
                            summary_parts.append(f"🖼️ Images: {len(attached_images)} file(s)")
                            for i, img in enumerate(attached_images[:3], 1):  # Show first 3 images
                                if isinstance(img, dict):
                                    filename = img.get('filename', f'image_{i}.png')
                                    summary_parts.append(f"  📷 {filename}")
                            if len(attached_images) > 3:
                                summary_parts.append(f"  ... and {len(attached_images) - 3} more")
                        
                        if attached_files:
                            files_info = []
                            folders_info = []
                            
                            for file_info in attached_files:
                                if isinstance(file_info, dict):
                                    relative_path = file_info.get('relative_path', 'unknown')
                                    file_type = file_info.get('type', 'unknown')
                                    if file_type == 'file':
                                        files_info.append(relative_path)
                                    elif file_type == 'folder':
                                        folders_info.append(relative_path)
                            
                            if folders_info:
                                summary_parts.append(f"📁 Folders: {len(folders_info)} item(s)")
                                for folder in folders_info[:3]:  # Show first 3 folders
                                    summary_parts.append(f"  📁 {folder}")
                                if len(folders_info) > 3:
                                    summary_parts.append(f"  ... and {len(folders_info) - 3} more")
                            
                            if files_info:
                                summary_parts.append(f"📄 Files: {len(files_info)} item(s)")
                                for file in files_info[:3]:  # Show first 3 files
                                    summary_parts.append(f"  📄 {file}")
                                if len(files_info) > 3:
                                    summary_parts.append(f"  ... and {len(files_info) - 3} more")
                        
                        display_message = "\n".join(summary_parts) if summary_parts else "Complex message with attachments"
                    except:
                        display_message = "Complex message with attachments"
                else:
                    # Simple messages - use raw content (same as waiting agent selection)
                    display_message = raw_message
                
                # Show message details
                details = [
                    f"Message ID: {msg_data.get('id', 'unknown')}",
                    f"From Agent: {msg_data.get('from_agent', 'unknown')}",
                    f"Delivered: {'Yes' if msg_data.get('delivered_all', False) else 'No'}",
                    f"Timestamp: {msg_data.get('timestamp', 'unknown')}",
                    "",
                    "📋 Message Content:",
                    display_message
                ]
                
                self.detail_display.setPlainText("\n".join(details))
        elif len(selected_items) > 1:
            # Multiple selection - show summary
            total = len(selected_items)
            delivered_count = 0
            for item in selected_items:
                msg_data = item.data(Qt.UserRole)
                if msg_data and msg_data.get("delivered_all", False):
                    delivered_count += 1
            
            summary = [
                f"Multiple Selection: {total} messages",
                f"Delivered: {delivered_count}",
                f"Pending: {total - delivered_count}",
                "",
                "Use 'Delete Selected' to remove these messages from queue."
            ]
            
            self.detail_display.setPlainText("\n".join(summary))
            self.participants_list.clear()
            
            # Disable delivery buttons for multi-selection
            self.deliver_to_1_btn.setEnabled(False)
            self.deliver_to_2_btn.setEnabled(False)
        else:
            # No selection
            self.detail_display.setPlainText("No message selected")
            self.participants_list.clear()
            self.deliver_to_1_btn.setEnabled(False)
            self.deliver_to_2_btn.setEnabled(False)
    

    
    
    def broadcast_message(self):
        """Broadcast selected message to all participants"""
        if not hasattr(self, 'selected_message'):
            QMessageBox.warning(self, "Warning", "Please select a message first!")
            return
        conv_id = self.selected_message.get("conversation_id")
        from_agent = self.selected_message.get("from_agent", "")
        targets = [self.participants_list.item(i).text() for i in range(self.participants_list.count()) if self.participants_list.item(i).text() != from_agent]
        self._send_to_participants(conv_id, targets)

    def send_selected_message(self):
        """Send message to selected participants"""
        if not hasattr(self, 'selected_message'):
            QMessageBox.warning(self, "Warning", "Please select a message first!")
            return
        targets = [item.text() for item in self.participants_list.selectedItems()]
        if not targets:
            QMessageBox.warning(self, "Warning", "Please select at least one participant!")
            return
        conv_id = self.selected_message.get("conversation_id")
        self._send_to_participants(conv_id, targets)

    def _send_to_participants(self, conversation_id: str, targets: List[str]):
        message_content = self.selected_message.get("message", "")
        formatted_message = self._format_message_for_delivery(message_content, continue_chat=True, source="agent")
        success = self.flow_manager.deliver_message_to_participants(conversation_id, targets, formatted_message, self.selected_message.get("id", ""))
        if success:
            self.status_label.setText(f"✅ Message delivered to {', '.join(targets)}")
            self.status_label.setStyleSheet(Styles.get_status_style("success"))
            self.status_reset_timer.start(3000)
            self.refresh_data()
        else:
            QMessageBox.warning(self, "Warning", "No target agents are currently waiting")

    def _on_participant_selection(self):
        if self.participants_list.selectedItems():
            self.deliver_to_2_btn.setEnabled(True)
        else:
            self.deliver_to_2_btn.setEnabled(False)

    def _format_message_for_delivery(self, message_content: str, continue_chat: bool = True, source: str = None) -> str:
        """
        Format message with AI_INTERACTION tags for proper conversation flow
        
        Args:
            message_content: Original message content
            continue_chat: Whether to continue conversation (default True for agent-to-agent communication)
            source: Message source ("admin" or "agent"), auto-detected if None
        
        Returns:
            Formatted message with proper tags
        """
        # Check if message already has AI_INTERACTION tags
        if "<AI_INTERACTION_CONTINUE_CHAT>" in message_content:
            # Message already properly formatted - but may need to add SOURCE if missing
            if "<AI_INTERACTION_SOURCE>" not in message_content:
                # Detect source if not provided
                if source is None:
                    source = "admin" if "AI_Chat_Controller" in str(self.__class__) else "agent"
                
                # Insert SOURCE tag before CONTINUE_CHAT
                formatted_message = message_content.replace(
                    "<AI_INTERACTION_CONTINUE_CHAT>",
                    f"<AI_INTERACTION_SOURCE>{source}</AI_INTERACTION_SOURCE>\n<AI_INTERACTION_CONTINUE_CHAT>"
                )
                return formatted_message
            return message_content
        
        # Detect source if not provided
        if source is None:
            # Messages delivered through controller are typically admin messages
            # (either from AI Chat or admin forwarding agent messages with admin authority)
            source = "admin"
        
        # Add tags to maintain conversation flow
        formatted_message = message_content
        formatted_message += f"\n\n<AI_INTERACTION_SOURCE>{source}</AI_INTERACTION_SOURCE>"
        formatted_message += f"\n<AI_INTERACTION_CONTINUE_CHAT>{str(continue_chat).lower()}</AI_INTERACTION_CONTINUE_CHAT>"
        
        return formatted_message
    
    def clear_all_data(self):
        """Clear ALL data - complete reset"""
        reply = QMessageBox.question(
            self,
            "⚠️ Confirm Clear All",
            "This will DELETE ALL waiting agents and messages!\n\nThis action cannot be undone.\n\nAre you sure?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.flow_manager.clear_all_data()
                
                # Clear message details and disable buttons
                self.detail_display.setPlainText("All data cleared")
                self.deliver_to_1_btn.setEnabled(False)
                self.deliver_to_2_btn.setEnabled(False)
                
                # Clear selected data
                if hasattr(self, 'selected_message'):
                    delattr(self, 'selected_message')
                if hasattr(self, 'selected_waiting_id'):
                    delattr(self, 'selected_waiting_id')
                
                self.refresh_data()
                self.result = "All data cleared"
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Clear all failed: {str(e)}")
    
    def delete_selected_messages(self):
        """Delete selected messages from queue"""
        selected_items = self.message_queue_widget.selectedItems()
        
        if not selected_items:
            QMessageBox.information(self, "Info", "No messages selected!")
            return
        
        # Collect message IDs BEFORE showing dialog (avoid timer interference)
        message_ids_to_delete = []
        for item in selected_items:
            msg_data = item.data(Qt.UserRole)
            if msg_data and msg_data.get("id"):
                message_ids_to_delete.append(msg_data.get("id"))
        
        if not message_ids_to_delete:
            QMessageBox.warning(self, "Warning", "No valid messages to delete!")
            return
        
        # Confirm deletion
        count = len(message_ids_to_delete)
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete {count} selected message(s) from queue?\n\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Temporarily stop timer during deletion
                if hasattr(self, 'timer'):
                    self.timer.stop()
                
                # Check if currently displayed message will be deleted
                clear_details = False
                if hasattr(self, 'selected_message'):
                    current_msg_id = self.selected_message.get("id")
                    if current_msg_id in message_ids_to_delete:
                        clear_details = True
                
                # Delete messages from flow manager
                deleted_count = self.flow_manager.delete_messages(message_ids_to_delete)
                
                if deleted_count > 0:
                    # Clear message details if the displayed message was deleted
                    if clear_details:
                        self.detail_display.setPlainText("Selected message has been deleted")
                        self.deliver_to_1_btn.setEnabled(False)
                        self.deliver_to_2_btn.setEnabled(False)
                        if hasattr(self, 'selected_message'):
                            delattr(self, 'selected_message')
                    
                    # Update status with beautiful success styling
                    self.status_label.setText(f"🗑️ Deleted {deleted_count} message(s) successfully!")
                    self.status_label.setStyleSheet(Styles.get_status_style("success"))
                    
                    # Reset status after 3 seconds
                    self.status_reset_timer.start(3000)
                    
                    self.refresh_data()
                    self.result = f"Deleted {deleted_count} messages"
                else:
                    QMessageBox.warning(self, "Warning", "No messages were deleted!")
                    
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to delete messages: {str(e)}")
            finally:
                # Safely restart timer to prevent memory leaks
                self._safe_restart_timer()
    
    def select_all_messages(self):
        """Select all messages in queue"""
        for i in range(self.message_queue_widget.count()):
            item = self.message_queue_widget.item(i)
            if item and item.flags() & Qt.ItemIsEnabled:  # Only select enabled items
                item.setSelected(True)
        
        self._update_delete_button_state()
    
    def clear_message_selection(self):
        """Clear message selection"""
        self.message_queue_widget.clearSelection()
        self._update_delete_button_state()
        self.detail_display.setPlainText("No message selected")
        self.deliver_to_1_btn.setEnabled(False)
        self.deliver_to_2_btn.setEnabled(False)
    
    def _update_delete_button_state(self):
        """Update delete button enabled state based on selection"""
        selected_items = self.message_queue_widget.selectedItems()
        has_deletable_items = False
        
        for item in selected_items:
            msg_data = item.data(Qt.UserRole)
            if msg_data and msg_data.get("id"):  # Only deletable if has ID
                has_deletable_items = True
                break
        
        self.delete_selected_btn.setEnabled(has_deletable_items)

    def setup_timer(self):
        """Setup auto-refresh timer - optimized refresh for real-time updates"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_data)
        self.timer.start(1500)  # Refresh every 1.5 seconds for balanced real-time updates
        
        # Setup status reset timer
        self.status_reset_timer = QTimer()
        self.status_reset_timer.setSingleShot(True)
        self.status_reset_timer.timeout.connect(self._reset_status_label)
        
    def _safe_restart_timer(self):
        """Safely restart the main timer to prevent memory leaks"""
        if hasattr(self, 'timer') and self.timer:
            # Stop existing timer before restart to prevent multiple timers
            self.timer.stop()
            self.timer.start(1500)  # Use same interval as setup_timer
    
    def _reset_status_label(self):
        """Reset status label to default"""
        data = self.flow_manager.get_controller_data()
        conv_count = len(data.get("conversations", {}))
        queue_count = len(data.get("message_queue", []))
        timestamp_display = data.get("timestamp", "")[-8:] if data.get("timestamp") else ""

        self.status_label.setText(f"📊 {conv_count} conversations • {queue_count} pending messages • Last update: {timestamp_display}")
        self.status_label.setStyleSheet(Styles.get_status_label_style())
    
    def get_result(self) -> Optional[str]:
        """Get result of controller interaction"""
        return self.result
    
    def _on_splitter_moved(self, pos, index):
        """Handle splitter movement - save new sizes"""
        sizes = self.main_splitter.sizes()
        self.config_manager.save_splitter_sizes(sizes)
    
    def resizeEvent(self, event):
        """Handle window resize - save new geometry"""
        super().resizeEvent(event)
        self._save_window_geometry()
    
    def moveEvent(self, event):
        """Handle window move - save new geometry"""
        super().moveEvent(event)
        self._save_window_geometry()
    
    def _save_window_geometry(self):
        """Save current window geometry to config"""
        geometry = self.geometry()
        self.config_manager.save_window_geometry(
            geometry.width(),
            geometry.height(), 
            geometry.x(),
            geometry.y()
        )
    
    def open_ai_chat(self):
        """Open AI Chat dialog for direct communication with agents"""
        try:
            from ..chat_ui.chat_adapter import show_ai_chat_dialog
            
            # Show AI chat dialog
            message, continue_chat = show_ai_chat_dialog(self)
            
            if message:
                # Send message to both agents through flow manager WITH continue_chat setting
                success_count = self._send_message_to_both_agents(message, continue_chat)
                
                if success_count > 0:
                    self.status_label.setText(f"📨 Broadcast message sent to {success_count} agent(s)")
                    self.status_label.setStyleSheet(Styles.get_status_style("success"))
                    
                    # Reset status after 3 seconds
                    self.status_reset_timer.start(3000)
                else:
                    QMessageBox.warning(
                        self,
                        "No Recipients",
                        "No agents are currently waiting to receive messages.\n\n"
                        "Please ensure agents are connected and waiting before sending messages."
                    )
                
                # Refresh data to show new messages in queue
                self.refresh_data()
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "AI Chat Error",
                f"Failed to open AI Chat:\n{str(e)}"
            )
    
    def _send_message_to_both_agents(self, message: str, continue_chat: bool = True) -> int:
        """
        Send message to all waiting agents
        
        Args:
            message: Message content to send
            continue_chat: Whether to continue chat (from AI Chat dialog)
            
        Returns:
            Number of agents message was sent to
        """
        # FORMAT MESSAGE WITH CONTINUE_CHAT TAG FOR AI CHAT (ADMIN) → AGENTS
        formatted_message = self._format_message_for_delivery(message, continue_chat, source="admin")
        
        waiting_agents = self.flow_manager.get_waiting_agents()
        sent_count = 0
        
        for waiting_id, agent_data in waiting_agents.items():
            if agent_data.get("status") == "waiting":
                try:
                    # Deliver formatted message to this waiting agent (direct delivery, no queue)
                    if self.flow_manager.deliver_message_to_agent(waiting_id, formatted_message):
                        sent_count += 1
                        
                        # NOTE: Admin messages are NOT added to queue - they're delivered directly
                        # Only agent-to-agent messages need queue for routing
                        
                except Exception as e:
                    print(f"Failed to send to {waiting_id}: {str(e)}")
                    continue
        
        return sent_count

    def closeEvent(self, event):
        """Handle window close event - ensure complete cleanup"""
        # Save final geometry before closing
        self._save_window_geometry()
        
        # Complete timer cleanup to prevent memory leaks
        if hasattr(self, 'timer') and self.timer:
            self.timer.stop()
            self.timer.deleteLater()
            
        if hasattr(self, 'status_reset_timer') and self.status_reset_timer:
            self.status_reset_timer.stop()
            self.status_reset_timer.deleteLater()
            
        super().closeEvent(event)


def show_controller_ui() -> Optional[str]:
    """
    Shows the main controller UI and returns the result
    
    This function handles the QApplication instance to ensure
    the UI runs correctly.
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
        
    dialog = ControllerUI()
    dialog.exec_()  # Use exec_ for modal dialog behavior
    
    result = dialog.get_result()
    return result 
