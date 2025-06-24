# Image attachment widget for AI Interaction Tool
import os
import base64
import mimetypes
import uuid
import shutil
from pathlib import Path
from PyQt5 import QtWidgets, QtCore, QtGui
from .styles import (
    get_image_container_stylesheet,
    get_image_placeholder_stylesheet,
    get_image_scroll_stylesheet,
    get_image_preview_card_stylesheet,
    get_image_preview_label_stylesheet,
    get_image_filename_label_stylesheet,
    get_image_size_label_stylesheet,
    get_image_remove_button_stylesheet,
)
from ..utils.translations import get_translation
from .image_viewer import ImageViewerDialog

class DragDropImageWidget(QtWidgets.QWidget):
    """Widget với chức năng drag & drop cho hình ảnh"""
    
    imageDropped = QtCore.pyqtSignal(list)  # Signal phát ra khi có ảnh được drop
    placeholderClicked = QtCore.pyqtSignal()  # Signal phát ra khi click vào placeholder
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.parent_widget = parent  # Store parent reference for translations
        
        # Setup UI
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(2, 2, 2, 2)
        self.layout.setSpacing(0)
        
        # Image placeholder (shown when no images) - giống file approach  
        # Get placeholder text from parent if available
        if hasattr(self.parent_widget, '_get_translation'):
            placeholder_text = "📷 " + self.parent_widget._get_translation("image_placeholder")
        else:
            placeholder_text = "📷 Drag & drop images here or click here to select images"
        
        self.image_placeholder = QtWidgets.QLabel(placeholder_text)
        self.image_placeholder.setAlignment(QtCore.Qt.AlignCenter)
        self.image_placeholder.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.image_placeholder.setStyleSheet(get_image_placeholder_stylesheet())
        self.image_placeholder.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))  # Show pointer cursor on hover
        
        # Scroll area for image previews (hidden by default)
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setFixedHeight(292)
        self.scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet(get_image_scroll_stylesheet())
        self.scroll_area.setVisible(False)  # Hidden by default, show when images added
        
        # Scrollable widget
        self.scroll_widget = QtWidgets.QWidget()
        self.preview_layout = QtWidgets.QHBoxLayout(self.scroll_widget)
        self.preview_layout.setContentsMargins(2, 2, 2, 2)
        self.preview_layout.setSpacing(6)
        self.preview_layout.setAlignment(QtCore.Qt.AlignLeft)  # Left align for images
        
        self.scroll_area.setWidget(self.scroll_widget)
        
        # Add both to existing layout - they will share the space
        self.layout.addWidget(self.image_placeholder)
        self.layout.addWidget(self.scroll_area)
        
    def mousePressEvent(self, event):
        """Handle mouse click events"""
        if event.button() == QtCore.Qt.LeftButton:
            # Check if click is on the placeholder and it's visible
            if self.image_placeholder.isVisible():
                # Check if click position is within placeholder bounds
                placeholder_rect = self.image_placeholder.geometry()
                if placeholder_rect.contains(event.pos()):
                    self.placeholderClicked.emit()
                    return
        
        # Call parent handler for other clicks
        super().mousePressEvent(event)
        
    def dragEnterEvent(self, event):
        """Xử lý khi drag vào widget"""
        if event.mimeData().hasUrls():
            # Kiểm tra nếu có ít nhất một file là hình ảnh
            urls = event.mimeData().urls()
            image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.ico'}
            
            has_image = False
            for url in urls:
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    ext = Path(file_path).suffix.lower()
                    if ext in image_extensions:
                        has_image = True
                        break
            
            if has_image:
                event.acceptProposedAction()
                self.setStyleSheet("border: 2px dashed #a855f7; background-color: rgba(168, 85, 247, 0.1);")
            else:
                event.ignore()
        else:
            event.ignore()
    
    def dragLeaveEvent(self, event):
        """Xử lý khi drag rời khỏi widget"""
        self.setStyleSheet("")  # Reset style
    
    def dropEvent(self, event):
        """Xử lý khi drop file vào widget"""
        self.setStyleSheet("")  # Reset style
        
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.ico'}
            image_paths = []
            
            for url in urls:
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    ext = Path(file_path).suffix.lower()
                    if ext in image_extensions and os.path.exists(file_path):
                        image_paths.append(file_path)
            
            if image_paths:
                self.imageDropped.emit(image_paths)
                event.acceptProposedAction()
            else:
                event.ignore()
        else:
            event.ignore()


class ImageAttachmentWidget(QtWidgets.QWidget):
    """Widget đính kèm hình ảnh với đầy đủ chức năng"""
    
    def __init__(self, parent=None, language="en", translations=None, config_manager=None):
        super().__init__(parent)
        self.language = language
        self.translations = translations or {}
        self.config_manager = config_manager
        
        # Danh sách hình ảnh đính kèm
        self.attached_images = []
        
        # Setup UI
        self.init_ui()
        
        # Restore images from config after UI is ready
        QtCore.QTimer.singleShot(100, self.restore_images_from_config)
    
    def _get_translation(self, key):
        """Lấy bản dịch cho key dựa trên ngôn ngữ hiện tại"""
        if self.translations:
            lang_dict = self.translations.get(self.language, {})
            return lang_dict.get(key, key)
        else:
            return get_translation(self.language, key)
    
    def init_ui(self):
        """Khởi tạo giao diện người dùng"""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        
        # Image buttons row
        image_buttons_layout = QtWidgets.QHBoxLayout()
        image_buttons_layout.setSpacing(8)
        
        self.attach_image_btn = QtWidgets.QPushButton("📷 " + self._get_translation("attach_image_btn"), self)
        self.attach_image_btn.setObjectName("attachImageBtn")
        self.attach_image_btn.clicked.connect(self.attach_image)
        self.attach_image_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.attach_image_btn.setProperty("button-type", "success")
        
        self.clear_images_btn = QtWidgets.QPushButton("🗑️ " + self._get_translation("clear_images"), self)
        self.clear_images_btn.setObjectName("clearImagesBtn")
        self.clear_images_btn.clicked.connect(self.clear_all_images)
        self.clear_images_btn.setEnabled(False)
        self.clear_images_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.clear_images_btn.setProperty("button-type", "warning")
        
        image_buttons_layout.addWidget(self.attach_image_btn)
        image_buttons_layout.addWidget(self.clear_images_btn)
        
        # Add save images checkbox to same row
        self.save_images_checkbox = QtWidgets.QCheckBox(self._get_translation("save_images_checkbox"), self)
        
        # Load checkbox state from config
        if self.config_manager:
            saved_state = self.config_manager.get('ui_preferences.save_images_enabled', True)
            self.save_images_checkbox.setChecked(saved_state)
        else:
            self.save_images_checkbox.setChecked(True)  # Default to saving images
            
        self.save_images_checkbox.setToolTip(self._get_translation("save_images_tooltip"))
        
        # SAVE STATE REALTIME: Connect signal to save state when checkbox changes
        self.save_images_checkbox.stateChanged.connect(self._on_save_checkbox_changed)
        
        image_buttons_layout.addWidget(self.save_images_checkbox)
        
        image_buttons_layout.addStretch()
        
        layout.addLayout(image_buttons_layout)
        
        # Image slider container
        self.image_slider_container = QtWidgets.QFrame()
        self.image_slider_container.setFrameStyle(QtWidgets.QFrame.NoFrame)
        self.image_slider_container.setStyleSheet(get_image_container_stylesheet())
        self.image_slider_container.setVisible(True)
        self.image_slider_container.setFixedHeight(300)
        
        # Container layout
        slider_main_layout = QtWidgets.QVBoxLayout(self.image_slider_container)
        slider_main_layout.setContentsMargins(2, 2, 2, 2)
        slider_main_layout.setSpacing(0)
        
        # Drag & Drop Image Widget
        self.drag_drop_widget = DragDropImageWidget(self)
        self.drag_drop_widget.imageDropped.connect(self.handle_dropped_images)
        self.drag_drop_widget.placeholderClicked.connect(self.attach_image)  # Connect placeholder click to attach_image
        
        # Reference các thành phần từ drag_drop_widget
        self.image_scroll_area = self.drag_drop_widget.scroll_area
        self.image_scroll_widget = self.drag_drop_widget.scroll_widget
        self.image_preview_layout = self.drag_drop_widget.preview_layout
        self.image_placeholder = self.drag_drop_widget.image_placeholder
        
        self.image_scroll_area.wheelEvent = self.handle_scroll_wheel
        
        slider_main_layout.addWidget(self.drag_drop_widget)
        layout.addWidget(self.image_slider_container)
    
    def attach_image(self):
        """Mở dialog để chọn hình ảnh với detailed feedback"""
        file_dialog = QtWidgets.QFileDialog(self)
        file_dialog.setWindowTitle("Select Images")
        file_dialog.setFileMode(QtWidgets.QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.gif *.bmp *.webp)")
        
        if file_dialog.exec_():
            selected_files = file_dialog.selectedFiles()
            # Use attached-specific processing
            self.handle_attached_images(selected_files)
    
    def handle_attached_images(self, image_paths):
        """Xử lý khi có hình ảnh được attach từ file dialog với detailed feedback"""
        successful_adds = 0
        duplicate_count = 0
        invalid_count = 0
        
        for image_path in image_paths:
            try:
                # Check if already exists (duplicate)
                source_filename = Path(image_path).name
                if any(img.get('filename') == source_filename for img in self.attached_images):
                    duplicate_count += 1
                    continue
                
                # Try to add to database
                if self._add_image_to_database(image_path, "attached"):
                    successful_adds += 1
                else:
                    invalid_count += 1
                
            except Exception as e:
                invalid_count += 1
        
        # Update UI if any successful adds
        if successful_adds > 0:
            self.update_image_ui(auto_scroll=True)
        
        # Show detailed feedback message
        self._show_attachment_result_message(successful_adds, duplicate_count, invalid_count)
    
    def image_to_base64(self, image_path):
        """Convert image file to base64 string"""
        try:
            with open(image_path, 'rb') as img_file:
                return base64.b64encode(img_file.read()).decode('utf-8')
        except Exception as e:
            return None
    
    def get_image_media_type(self, image_path):
        """Get MIME type for image file"""
        mime_type, _ = mimetypes.guess_type(image_path)
        return mime_type or 'image/png'
    
    def add_image_preview(self, image_path):
        """Add simple, robust image preview"""
        # Create taller preview card with more info space
        preview_card = QtWidgets.QFrame()
        preview_card.setFixedSize(150, 170)
        preview_card.setFrameStyle(QtWidgets.QFrame.NoFrame)
        preview_card.setStyleSheet(get_image_preview_card_stylesheet())
        
        # Larger card layout with more space
        card_layout = QtWidgets.QVBoxLayout(preview_card)
        card_layout.setContentsMargins(8, 8, 8, 8)
        card_layout.setSpacing(6)
        
        # Larger image container
        image_container = QtWidgets.QWidget()
        image_container.setFixedSize(130, 100)
        image_container_layout = QtWidgets.QVBoxLayout(image_container)
        image_container_layout.setContentsMargins(0, 0, 0, 0)
        image_container_layout.setAlignment(QtCore.Qt.AlignCenter)
        
        # Larger image display
        image_display = QtWidgets.QLabel()
        image_display.setFixedSize(126, 96)
        image_display.setAlignment(QtCore.Qt.AlignCenter)
        image_display.setScaledContents(False)
        image_display.setStyleSheet(get_image_preview_label_stylesheet())
        
        # Add image to container với click functionality
        image_container_layout.addWidget(image_display)
        
        # Make image clickable để view larger
        image_display.mousePressEvent = lambda event: self.show_image_large(image_path)
        
        # Load and display image với better scaling
        try:
            pixmap = QtGui.QPixmap(image_path)
            if not pixmap.isNull():
                # Scale to fit larger display area với high quality
                scaled_pixmap = pixmap.scaled(122, 92, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                image_display.setPixmap(scaled_pixmap)
            else:
                image_display.setText("🖼️\nInvalid")
                image_display.setStyleSheet(image_display.styleSheet() + """
                    QLabel { color: #999; font-size: 11px; }
                """)
        except Exception as e:
            image_display.setText("⚠️\nError")
            image_display.setStyleSheet(image_display.styleSheet() + """
                QLabel { color: #ff5722; font-size: 11px; }
            """)
        
        # Add image container to card
        card_layout.addWidget(image_container)
        
        # Bottom info section với more details
        info_layout = QtWidgets.QVBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(3)
        
        # Filename row với remove button
        filename_row = QtWidgets.QHBoxLayout()
        filename_row.setContentsMargins(0, 0, 0, 0)
        filename_row.setSpacing(4)
        
        # Filename với bold styling - always use database filename
        filename = Path(image_path).name
        if len(filename) > 16:
            filename = filename[:13] + "..."
        
        filename_label = QtWidgets.QLabel(filename)
        filename_label.setStyleSheet(get_image_filename_label_stylesheet())
        filename_label.setToolTip(f"Database: {Path(image_path).name}")
        
        # Perfectly circular remove button with guaranteed circle
        remove_btn = QtWidgets.QPushButton("X")
        remove_btn.setStyleSheet(get_image_remove_button_stylesheet())
        
        # Store data in button for safe removal - avoid lambda closure
        remove_btn.setProperty("image_path", image_path)
        remove_btn.setProperty("preview_widget", preview_card)
        remove_btn.clicked.connect(self._handle_remove_button_click)
        
        # Add to filename row
        filename_row.addWidget(filename_label)
        filename_row.addStretch()
        filename_row.addWidget(remove_btn)
        
        # Add image size info
        try:
            file_size = os.path.getsize(image_path)
            if file_size < 1024:
                size_text = f"{file_size} B"
            elif file_size < 1024 * 1024:
                size_text = f"{file_size // 1024} KB"
            else:
                size_text = f"{file_size // (1024 * 1024)} MB"
        except:
            size_text = "Unknown size"
        
        size_label = QtWidgets.QLabel(size_text)
        size_label.setStyleSheet(get_image_size_label_stylesheet())
        
        # Add all info to layout
        info_layout.addLayout(filename_row)
        info_layout.addWidget(size_label)
        
        card_layout.addLayout(info_layout)
        
        # Add to preview layout
        self.image_preview_layout.addWidget(preview_card)
        
        # Update UI with auto-scroll for new images (this will handle placeholder hide/show)
        self.update_image_ui(auto_scroll=True)
    
    def _handle_remove_button_click(self):
        """Safe handler for remove button clicks"""
        sender = self.sender()
        if sender:
            image_path = sender.property("image_path")
            preview_widget = sender.property("preview_widget")
            if image_path and preview_widget:
                self.remove_image(image_path, preview_widget)
    
    def remove_image(self, image_path, preview_widget):
        """Remove image from preview and storage"""
        try:
            # Remove from database first
            database_success = self._remove_image_from_database(image_path)
            
            # Always remove UI element regardless of database success
            # This ensures UI stays in sync with memory state
            if preview_widget and preview_widget.parent():
                preview_widget.setParent(None)
                preview_widget.deleteLater()
            
            # Update UI safely
            QtCore.QTimer.singleShot(0, self.update_image_ui)
            
            # Save updated config if saving is enabled
            if hasattr(self, 'save_images_checkbox') and self.save_images_checkbox.isChecked():
                QtCore.QTimer.singleShot(100, self.save_images_to_config)
            
        except Exception as e:
            # Ensure UI is updated even if removal fails
            QtCore.QTimer.singleShot(0, self.update_image_ui)
    
    def clear_all_images(self):
        """Xóa tất cả hình ảnh đã đính kèm"""
        if not self.attached_images:
            QtWidgets.QMessageBox.information(
                self, 
                self._get_translation("no_images_title"), 
                self._get_translation("no_images_message")
            )
            return
        
        # Xác nhận xóa
        reply = QtWidgets.QMessageBox.question(
            self, 
            self._get_translation("clear_all_images_title"), 
            self._get_translation("clear_all_images_message").format(count=len(self.attached_images)),
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            # Show loading for bulk operation
            self._show_loading_state("Clearing all images...")
            
            # Remove all images from database
            successful_removals = 0
            total_images = len(self.attached_images)
            
            for img in self.attached_images.copy():
                if self._remove_image_from_database(img.get('path')):
                    successful_removals += 1
            
            # Only clear UI if all database operations succeeded
            if successful_removals == total_images:
                # Remove all preview widgets from layout
                while self.image_preview_layout.count() > 0:
                    item = self.image_preview_layout.takeAt(0)
                    if item.widget():
                        item.widget().setParent(None)
                        

            
            # Hide loading state
            self._hide_loading_state()
            
            # Update UI
            self.update_image_ui()
            
            # Save updated config
            if hasattr(self, 'save_images_checkbox') and self.save_images_checkbox.isChecked():
                self.save_images_to_config()
    
    def handle_dropped_images(self, image_paths):
        """Xử lý khi có hình ảnh được drop vào widget với detailed feedback"""
        successful_adds = 0
        failed_adds = 0
        duplicate_count = 0
        invalid_count = 0
        
        for image_path in image_paths:
            try:
                # Check if already exists (duplicate)
                source_filename = Path(image_path).name
                if any(img.get('filename') == source_filename for img in self.attached_images):
                    duplicate_count += 1
                    continue
                
                # Try to add to database
                if self._add_image_to_database(image_path, "dropped"):
                    successful_adds += 1
                else:
                    invalid_count += 1
                
            except Exception as e:
                invalid_count += 1
        
        # Update UI if any successful adds
        if successful_adds > 0:
            self.update_image_ui(auto_scroll=True)
        
        # Show detailed feedback message
        self._show_attachment_result_message(successful_adds, duplicate_count, invalid_count)
    
    def _show_attachment_result_message(self, successful, duplicates, invalid):
        """Show detailed result message only when there are problems"""
        # Only show message if there are duplicates or errors
        if duplicates == 0 and invalid == 0:
            # Pure success - no message needed
            return
        
        message_parts = []
        
        if successful > 0:
            message_parts.append(
                self._get_translation("image_result_success").format(count=successful)
            )
        
        if duplicates > 0:
            message_parts.append(
                self._get_translation("image_result_duplicates").format(count=duplicates)
            )
        
        if invalid > 0:
            message_parts.append(
                self._get_translation("image_result_invalid").format(count=invalid)
            )
        
        final_message = "\n".join(message_parts)
        
        # Use warning if any failures, info if just duplicates
        if invalid > 0:
            QtWidgets.QMessageBox.warning(
                self,
                self._get_translation("image_result_title"),
                final_message
            )
        else:
            QtWidgets.QMessageBox.information(
                self,
                self._get_translation("image_result_title"),
                final_message
            )
    
    def show_image_large(self, image_path):
        """Show image in ultra-modern viewer dialog with advanced zoom controls"""
        dialog = ImageViewerDialog(
            image_path=image_path,
            parent=self, 
            translations=self.translations, 
            language=self.language
        )
        dialog.exec_()

    def handle_scroll_wheel(self, event):
        """Handle smooth horizontal scrolling trong image slider"""
        if event.modifiers() == QtCore.Qt.NoModifier:
            # Horizontal scroll với mouse wheel
            delta = event.angleDelta().y()
            scroll_bar = self.image_scroll_area.horizontalScrollBar()
            scroll_bar.setValue(scroll_bar.value() - delta // 8)
            event.accept()
        else:
            # Allow parent to handle other scroll events
            event.ignore()

    def update_image_ui(self, auto_scroll=False):
        """Update image slider UI and button text - container always visible"""
        has_images = len(self.attached_images) > 0
        
        # Update button states
        self.clear_images_btn.setEnabled(has_images)
        
        # Show/hide placeholder và scroll area giống file approach
        self.image_placeholder.setVisible(not has_images)
        self.image_scroll_area.setVisible(has_images)
        
        # Update attach button text with count (ensure not in loading state)
        if has_images:
            count = len(self.attached_images)
            self.attach_image_btn.setText(f"📷 {self._get_translation('attach_image_btn')} ({count})")
        else:
            self.attach_image_btn.setText(f"📷 {self._get_translation('attach_image_btn')}")
        
        # Restore placeholder text if no images (fix loading state bug)
        if not has_images and hasattr(self, 'image_placeholder'):
            placeholder_text = "📷 " + self._get_translation("image_placeholder")
            self.image_placeholder.setText(placeholder_text)
        
        # Auto-scroll to show newest image only when adding new images
        if has_images and auto_scroll:
            QtCore.QTimer.singleShot(100, lambda: self.image_scroll_area.horizontalScrollBar().setValue(
                self.image_scroll_area.horizontalScrollBar().maximum()
            ))
    
    def get_attached_images(self):
        """Return list of attached images"""
        return self.attached_images
    
    def save_images_to_config(self):
        """Save attached images to config if checkbox is checked"""
        if self.config_manager and hasattr(self, 'save_images_checkbox'):
            if self.save_images_checkbox.isChecked():
                # Save database image metadata
                image_data = []
                for img in self.attached_images:
                    # SECURITY: Only store database-relative information, no external paths
                    image_data.append({
                        "db_path": img.get("path"),
                        "filename": img.get("filename"),
                        "media_type": img.get("media_type", "image/png"),
                        "source_type": img.get("source_type", "attached"),
                        "db_filename": img.get("db_filename"),
                        "relative_db_path": img.get("relative_db_path", os.path.basename(img.get("path", "")))
                    })
                
                self.config_manager.set('last_attached_images', image_data)
            else:
                # Clear saved images if checkbox unchecked and clean database
                self.config_manager.set('last_attached_images', [])
                self._cleanup_all_database_images()
                
            self.config_manager.save_config()
    
    def _cleanup_all_database_images(self):
        """Clean up all images in database when save is disabled"""
        try:
            user_images_dir = self._get_user_images_dir()
            if os.path.exists(user_images_dir):
                for filename in os.listdir(user_images_dir):
                    if filename.startswith(("pasted_", "attached_", "dropped_")):
                        file_path = os.path.join(user_images_dir, filename)
                        os.remove(file_path)
                        pass
        except Exception as e:
            pass
    
    def _get_user_images_dir(self):
        """Get or create user_images directory"""
        # Get absolute path to this file
        current_file = os.path.abspath(__file__)
        # Navigate up from agent_comm/chat_ui/ui/image_attachment.py to Utils/
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file))))
        
        # Create user_images directory in project root
        user_images_dir = os.path.join(project_root, "user_images")
        
        # Create directory if it doesn't exist
        os.makedirs(user_images_dir, exist_ok=True)
        
        return user_images_dir
    
    def _cleanup_permanent_copies(self):
        """Clean up permanent copies of images"""
        try:
            user_images_dir = self._get_user_images_dir()
            if os.path.exists(user_images_dir):
                # Only remove pasted image files, not all files
                for filename in os.listdir(user_images_dir):
                    if filename.startswith("pasted_"):
                        file_path = os.path.join(user_images_dir, filename)
                        os.remove(file_path)
                        pass
        except Exception as e:
            pass
    
    def _add_image_to_database(self, source_path, source_type="attached"):
        """
        Unified method to add image to database (user_images directory)
        Args:
            source_path: Path to source image file
            source_type: "attached", "dropped", or "pasted"
        Returns:
            bool: True if successfully added, False otherwise
        """
        try:
            # Check for duplicates using filename only (security: no full paths stored)
            source_filename = Path(source_path).name
            if any(img.get('filename') == source_filename for img in self.attached_images):
                return False
            
            # Show loading state
            self._show_loading_state(f"Adding {source_type} image...")
            
            # Get user_images directory
            user_images_dir = self._get_user_images_dir()
            
            # Generate unique filename
            original_filename = Path(source_path).name
            file_ext = Path(source_path).suffix
            unique_id = str(uuid.uuid4())[:8]
            
            # Create database filename based on source type
            if source_type == "pasted":
                db_filename = f"pasted_{unique_id}{file_ext}"
            elif source_type == "dropped":
                db_filename = f"dropped_{unique_id}_{original_filename}"
            else:  # attached
                db_filename = f"attached_{unique_id}_{original_filename}"
            
            db_path = os.path.join(user_images_dir, db_filename)
            
            # Copy image to database with original quality
            shutil.copy2(source_path, db_path)
            
            # Verify database file exists before proceeding
            if not os.path.exists(db_path):
                self._hide_loading_state()
                return False
            
            # Convert to base64 from database copy
            base64_data = self.image_to_base64(db_path)
            if not base64_data:
                # Clean up failed copy
                if os.path.exists(db_path):
                    os.remove(db_path)
                self._hide_loading_state()
                return False
            
            # Add to attached_images list - SECURITY: Only store relative paths in user_images
            image_info = {
                "path": db_path,  # Database path (only within user_images)
                "filename": original_filename,  # Original filename for display
                "base64_data": base64_data,
                "media_type": self.get_image_media_type(db_path),
                "source_type": source_type,
                "db_filename": db_filename,  # For database management (relative)
                "relative_db_path": os.path.basename(db_path)  # SECURITY: Only relative path stored
            }
            
            self.attached_images.append(image_info)
            
            # Add to UI only after database operation is complete
            self.add_image_preview(db_path)
            
            # Hide loading state
            self._hide_loading_state()
            
            return True
            
        except Exception as e:
            self._hide_loading_state()
            return False
    
    def _remove_image_from_database(self, db_path):
        """Remove image from database and storage"""
        try:
            # Show loading state
            self._show_loading_state("Removing image...")
            
            # Remove from attached_images first
            original_count = len(self.attached_images)
            self.attached_images = [img for img in self.attached_images if img.get('path') != db_path]
            
            # Verify removal from memory
            if len(self.attached_images) == original_count:
                self._hide_loading_state()
                return False
            
            # Remove physical file from database
            if os.path.exists(db_path) and "user_images" in db_path:
                os.remove(db_path)
                
                # Verify file is actually removed
                if os.path.exists(db_path):
                    self._hide_loading_state()
                    return False
            
            # Hide loading state
            self._hide_loading_state()
            return True
            
        except Exception as e:
            self._hide_loading_state()
            return False
    
    def _show_loading_state(self, message="Loading..."):
        """Show loading state in UI"""
        try:
            # Disable buttons during loading
            if hasattr(self, 'attach_image_btn'):
                self.attach_image_btn.setEnabled(False)
                self.attach_image_btn.setText(f"⏳ {message}")
            
            if hasattr(self, 'clear_images_btn'):
                self.clear_images_btn.setEnabled(False)
                
            # Show loading in placeholder if visible
            if hasattr(self, 'image_placeholder') and self.image_placeholder.isVisible():
                self.image_placeholder.setText(f"⏳ {message}")
                
        except Exception as e:
            pass
    
    def _hide_loading_state(self):
        """Hide loading state and restore UI"""
        try:
            # Re-enable buttons
            if hasattr(self, 'attach_image_btn'):
                self.attach_image_btn.setEnabled(True)
            
            if hasattr(self, 'clear_images_btn'):
                self.clear_images_btn.setEnabled(True)  # Will be properly set by update_image_ui
                
            # Don't manually set text here - let update_image_ui handle it properly
            # This prevents conflicts between loading state and UI update
                
        except Exception as e:
            pass
    
    def _remove_permanent_copy(self, image_path):
        """Remove a specific permanent copy when image is removed - DEPRECATED"""
        # This method is now handled by _remove_image_from_database
        pass

    def restore_images_from_config(self):
        """Restore images from config"""
        if not self.config_manager:
            return
            
        saved_images = self.config_manager.get('last_attached_images', [])
        
        if not saved_images:
            return
            
        # Load saved checkbox state - default to True if not set
        save_enabled = self.config_manager.get('ui_preferences.save_images_enabled', True)
        
        if hasattr(self, 'save_images_checkbox'):
            self.save_images_checkbox.setChecked(save_enabled)
            
        # Only restore if save is enabled
        if not save_enabled:
            return
            
        # Show loading for restore operation
        self._show_loading_state(f"Restoring {len(saved_images)} images...")
        
        # Debug disabled
        
        restored_count = 0
        for i, img_data in enumerate(saved_images):
            db_path = img_data.get("db_path")
            
            if db_path and os.path.exists(db_path):
                try:
                    # Convert to base64 from database
                    base64_data = self.image_to_base64(db_path)
                    if base64_data:
                        # Restore full image info - SECURITY: No external paths stored
                        image_info = {
                            "path": db_path,
                            "filename": img_data.get("filename", Path(db_path).name),
                            "base64_data": base64_data,
                            "media_type": img_data.get("media_type", "image/png"),
                            "source_type": img_data.get("source_type", "attached"),
                            "db_filename": img_data.get("db_filename"),
                            "relative_db_path": img_data.get("relative_db_path", os.path.basename(db_path))
                        }
                        
                        self.attached_images.append(image_info)
                        self.add_image_preview(db_path)
                        restored_count += 1
                except Exception as e:
                    pass
        
        # Hide loading state
        self._hide_loading_state()
                    
        if restored_count > 0:
            self.update_image_ui()
    
    def _show_debug_message(self, title, message):
        """Show debug message in a dialog"""
        try:
            msg_box = QtWidgets.QMessageBox(self)
            msg_box.setWindowTitle(title)
            msg_box.setText(message)
            msg_box.setIcon(QtWidgets.QMessageBox.Information)
            msg_box.exec_()
        except Exception as e:
            pass

    def _on_save_checkbox_changed(self, state):
        """Handle save images checkbox state change - save to config realtime"""
        try:
            if self.config_manager:
                # Save checkbox state immediately when changed
                is_checked = state == QtCore.Qt.Checked
                self.config_manager.set('ui_preferences.save_images_enabled', is_checked)
                self.config_manager.save_config()
                
                # If checkbox is unchecked, clean database immediately
                if not is_checked:
                    self._cleanup_all_database_images()
                    
        except Exception as e:
            pass

    def set_language(self, language):
        """Update language and refresh UI text"""
        self.language = language
        self.attach_image_btn.setText("📷 " + self._get_translation("attach_image_btn"))
        self.clear_images_btn.setText("🗑️ " + self._get_translation("clear_images"))
        self.save_images_checkbox.setText(self._get_translation("save_images_checkbox"))
        self.save_images_checkbox.setToolTip(self._get_translation("save_images_tooltip"))
        
        # Update placeholder text in drag drop widget
        placeholder_text = "📷 " + self._get_translation("image_placeholder")
        self.image_placeholder.setText(placeholder_text) 