"""
Advanced Image Viewer Component for AI Interaction Tool
"""

import os
from pathlib import Path
from PyQt5 import QtWidgets, QtCore, QtGui

from .styles import (
    get_image_viewer_dialog_stylesheet,
    get_image_viewer_header_stylesheet, 
    get_image_viewer_zoom_container_stylesheet,
    get_image_viewer_zoom_icon_stylesheet,
    get_image_viewer_zoom_button_stylesheet,
    get_image_viewer_zoom_label_stylesheet,
    get_image_viewer_fit_button_stylesheet,
    get_image_viewer_reset_button_stylesheet,
    get_image_viewer_scroll_area_stylesheet,
    get_image_viewer_image_label_stylesheet,
    get_image_viewer_footer_container_stylesheet,
    get_image_viewer_info_label_stylesheet,
    get_image_viewer_shortcuts_label_stylesheet,
    get_image_viewer_close_button_stylesheet
)


class ImageViewerDialog(QtWidgets.QDialog):
    """Ultra-modern image viewer dialog with advanced zoom controls"""
    
    def __init__(self, image_path, parent=None, translations=None, language="en"):
        super().__init__(parent)
        self.image_path = image_path
        self.translations = translations or {}
        self.language = language
        self.current_zoom = 1.0
        self.is_dragging = False
        self.last_pan_point = QtCore.QPoint()
        self.original_pixmap = None
        
        self.init_ui()
        self.setup_image()
        self.setup_events()
        
    def _get_translation(self, key):
        """Get translation for given key"""
        if self.translations and self.language in self.translations:
            return self.translations[self.language].get(key, key)
        return key
        
    def init_ui(self):
        """Initialize the ultra-modern UI"""
        self.setWindowTitle(f"🖼️ {Path(self.image_path).name}")
        
        # Set dynamic size to 70% of screen dimensions
        screen = QtWidgets.QApplication.desktop().screenGeometry()
        dialog_width = int(screen.width() * 0.7)
        dialog_height = int(screen.height() * 0.7)
        self.setMinimumSize(dialog_width, dialog_height)
        self.resize(dialog_width, dialog_height)
        
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        
        # Modern dark theme for dialog
        self.setStyleSheet(get_image_viewer_dialog_stylesheet())
        
        # Main layout with modern spacing
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)
        
        # Modern header with title
        self.create_header(main_layout)
        
        # Ultra-modern zoom control bar
        self.create_zoom_controls(main_layout)
        
        # Ultra-modern scroll area
        self.create_image_area(main_layout)
        
        # Ultra-modern footer
        self.create_footer(main_layout)
        
    def create_header(self, main_layout):
        """Create modern header with title"""
        header_layout = QtWidgets.QHBoxLayout()
        header_layout.setSpacing(15)
        
        # Elegant title
        title_label = QtWidgets.QLabel(f"🎨 {Path(self.image_path).name}")
        title_label.setStyleSheet(get_image_viewer_header_stylesheet())
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        main_layout.addLayout(header_layout)
        
    def create_zoom_controls(self, main_layout):
        """Create ultra-modern zoom control bar"""
        zoom_container = QtWidgets.QFrame()
        zoom_container.setStyleSheet(get_image_viewer_zoom_container_stylesheet())
        
        zoom_layout = QtWidgets.QHBoxLayout(zoom_container)
        zoom_layout.setContentsMargins(15, 10, 15, 10)
        zoom_layout.setSpacing(12)
        
        # Zoom icon
        zoom_title = QtWidgets.QLabel("🔍")
        zoom_title.setStyleSheet(get_image_viewer_zoom_icon_stylesheet())
        
        # Zoom out button
        self.zoom_out_btn = QtWidgets.QPushButton("−")
        self.zoom_out_btn.setStyleSheet(get_image_viewer_zoom_button_stylesheet())
        self.zoom_out_btn.setToolTip(self._get_translation("image_viewer_zoom_out_tooltip"))
        
        # Zoom level display
        self.zoom_label = QtWidgets.QLabel("100%")
        self.zoom_label.setAlignment(QtCore.Qt.AlignCenter)
        self.zoom_label.setMinimumWidth(55)
        self.zoom_label.setStyleSheet(get_image_viewer_zoom_label_stylesheet())
        
        # Zoom in button
        self.zoom_in_btn = QtWidgets.QPushButton("+")
        self.zoom_in_btn.setStyleSheet(get_image_viewer_zoom_button_stylesheet())
        self.zoom_in_btn.setToolTip(self._get_translation("image_viewer_zoom_in_tooltip"))
        
        # Fit to window button
        self.fit_btn = QtWidgets.QPushButton("⌂")
        self.fit_btn.setStyleSheet(get_image_viewer_fit_button_stylesheet())
        self.fit_btn.setToolTip(self._get_translation("image_viewer_fit_tooltip"))
        
        # Reset to 100% button
        self.reset_btn = QtWidgets.QPushButton("⌘")
        self.reset_btn.setStyleSheet(get_image_viewer_reset_button_stylesheet())
        self.reset_btn.setToolTip(self._get_translation("image_viewer_reset_tooltip"))
        
        # Add elements to zoom layout
        zoom_layout.addWidget(zoom_title)
        zoom_layout.addWidget(self.zoom_out_btn)
        zoom_layout.addWidget(self.zoom_label)
        zoom_layout.addWidget(self.zoom_in_btn)
        zoom_layout.addStretch()
        zoom_layout.addWidget(self.fit_btn)
        zoom_layout.addWidget(self.reset_btn)
        
        main_layout.addWidget(zoom_container)
        
    def create_image_area(self, main_layout):
        """Create ultra-modern scroll area and image display"""
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet(get_image_viewer_scroll_area_stylesheet())
        
        # Ultra-modern image display
        self.image_label = QtWidgets.QLabel()
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)
        self.image_label.setStyleSheet(get_image_viewer_image_label_stylesheet())
        
        self.scroll_area.setWidget(self.image_label)
        main_layout.addWidget(self.scroll_area)
        
    def create_footer(self, main_layout):
        """Create ultra-modern footer with info and controls"""
        footer_container = QtWidgets.QFrame()
        footer_container.setStyleSheet(get_image_viewer_footer_container_stylesheet())
        
        footer_layout = QtWidgets.QHBoxLayout(footer_container)
        footer_layout.setContentsMargins(20, 12, 20, 12)
        footer_layout.setSpacing(15)
        
        # Image info will be added after loading image
        self.info_label = None
        
        # Keyboard shortcuts info
        shortcuts_label = QtWidgets.QLabel(f"⌨️ {self._get_translation('image_viewer_shortcuts')}")
        shortcuts_label.setStyleSheet(get_image_viewer_shortcuts_label_stylesheet())
        footer_layout.addWidget(shortcuts_label)
        
        footer_layout.addStretch()
        
        # Close button
        close_btn = QtWidgets.QPushButton("✕")
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet(get_image_viewer_close_button_stylesheet())
        close_btn.setToolTip(self._get_translation("image_viewer_close_tooltip"))
        
        footer_layout.addWidget(close_btn)
        main_layout.addWidget(footer_container)
        
        # Store footer layout for later adding image info
        self.footer_layout = footer_layout
        
    def setup_image(self):
        """Load and setup the image"""
        self.original_pixmap = QtGui.QPixmap(self.image_path)
        if self.original_pixmap.isNull():
            self.image_label.setText(self._get_translation("image_viewer_unable_load"))
            self.zoom_out_btn.setEnabled(False)
            self.zoom_in_btn.setEnabled(False)
            self.fit_btn.setEnabled(False)
            self.reset_btn.setEnabled(False)
        else:
            # Add image info to footer
            self.add_image_info()
            # Fit to window initially
            QtCore.QTimer.singleShot(100, self.fit_to_window)
            
    def add_image_info(self):
        """Add image info to footer"""
        if self.original_pixmap and not self.original_pixmap.isNull():
            size_info = f"📐 {self.original_pixmap.width()} × {self.original_pixmap.height()} px"
            try:
                file_size = os.path.getsize(self.image_path)
                if file_size < 1024:
                    size_text = f"{file_size} B"
                elif file_size < 1024 * 1024:
                    size_text = f"{file_size // 1024} KB"
                else:
                    size_text = f"{file_size // (1024 * 1024)} MB"
                size_info += f"  •  💾 {size_text}"
            except:
                pass
                
            self.info_label = QtWidgets.QLabel(size_info)
            self.info_label.setStyleSheet(get_image_viewer_info_label_stylesheet())
            # Insert at beginning of footer layout
            self.footer_layout.insertWidget(0, self.info_label)
            
    def setup_events(self):
        """Setup all event handlers"""
        # Connect zoom controls
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        self.fit_btn.clicked.connect(self.fit_to_window)
        self.reset_btn.clicked.connect(self.reset_zoom)
        
        # Custom event handlers for scroll area
        self.scroll_area.wheelEvent = self.wheel_event
        self.scroll_area.mousePressEvent = self.mouse_press_event
        self.scroll_area.mouseMoveEvent = self.mouse_move_event
        self.scroll_area.mouseReleaseEvent = self.mouse_release_event
        self.scroll_area.enterEvent = self.enter_event
        self.scroll_area.leaveEvent = self.leave_event
        
    def update_image(self):
        """Update image display with current zoom"""
        if self.original_pixmap.isNull():
            return
            
        # Calculate new size
        new_size = self.original_pixmap.size() * self.current_zoom
        
        # Scale image with high quality
        scaled_pixmap = self.original_pixmap.scaled(
            new_size,
            QtCore.Qt.KeepAspectRatio,
            QtCore.Qt.SmoothTransformation
        )
        
        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.resize(scaled_pixmap.size())
        
        # Update zoom label
        self.zoom_label.setText(f"{int(self.current_zoom * 100)}%")
        
        # Enable/disable buttons based on zoom level
        self.zoom_out_btn.setEnabled(self.current_zoom > 0.1)  # Min 10%
        self.zoom_in_btn.setEnabled(self.current_zoom < 20.0)   # Max 2000%
    
    def zoom_in(self):
        """Zoom in with smooth, gentle increments"""
        if self.current_zoom < 20.0:
            self.current_zoom = min(20.0, self.current_zoom * 1.15)
            self.update_image()
    
    def zoom_out(self):
        """Zoom out with smooth, gentle decrements"""
        if self.current_zoom > 0.1:
            self.current_zoom = max(0.1, self.current_zoom / 1.15)
            self.update_image()
    
    def fit_to_window(self):
        """Fit image to window size"""
        if self.original_pixmap.isNull():
            return
            
        # Get available space (scroll area size minus margins)
        available_size = self.scroll_area.size() - QtCore.QSize(40, 40)
        
        # Calculate scale to fit
        scale_x = available_size.width() / self.original_pixmap.width()
        scale_y = available_size.height() / self.original_pixmap.height()
        self.current_zoom = min(scale_x, scale_y, 1.0)  # Don't enlarge beyond 100%
        
        self.update_image()
    
    def reset_zoom(self):
        """Reset to 100% zoom"""
        self.current_zoom = 1.0
        self.update_image()
    
    def wheel_event(self, event):
        """Handle wheel events for zoom with Ctrl"""
        if event.modifiers() == QtCore.Qt.ControlModifier:
            # Ctrl + Scroll for zoom
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.accept()
        else:
            # Normal scroll behavior
            QtWidgets.QScrollArea.wheelEvent(self.scroll_area, event)
    
    def mouse_press_event(self, event):
        """Handle mouse press for panning"""
        if event.button() == QtCore.Qt.LeftButton:
            self.is_dragging = True
            self.last_pan_point = event.pos()
            self.scroll_area.setCursor(QtCore.Qt.ClosedHandCursor)
            event.accept()
        else:
            QtWidgets.QScrollArea.mousePressEvent(self.scroll_area, event)
    
    def mouse_move_event(self, event):
        """Handle mouse move for panning"""
        if self.is_dragging and event.buttons() == QtCore.Qt.LeftButton:
            # Calculate pan delta
            delta = event.pos() - self.last_pan_point
            self.last_pan_point = event.pos()
            
            # Update scroll position
            h_scroll = self.scroll_area.horizontalScrollBar()
            v_scroll = self.scroll_area.verticalScrollBar()
            
            h_scroll.setValue(h_scroll.value() - delta.x())
            v_scroll.setValue(v_scroll.value() - delta.y())
            
            event.accept()
        else:
            QtWidgets.QScrollArea.mouseMoveEvent(self.scroll_area, event)
    
    def mouse_release_event(self, event):
        """Handle mouse release for panning"""
        if event.button() == QtCore.Qt.LeftButton:
            self.is_dragging = False
            self.scroll_area.setCursor(QtCore.Qt.OpenHandCursor)
            event.accept()
        else:
            QtWidgets.QScrollArea.mouseReleaseEvent(self.scroll_area, event)
    
    def enter_event(self, event):
        """Set hand cursor when entering scroll area"""
        self.scroll_area.setCursor(QtCore.Qt.OpenHandCursor)
        QtWidgets.QScrollArea.enterEvent(self.scroll_area, event)
    
    def leave_event(self, event):
        """Reset cursor when leaving scroll area"""
        self.scroll_area.setCursor(QtCore.Qt.ArrowCursor)
        QtWidgets.QScrollArea.leaveEvent(self.scroll_area, event)
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        if event.key() == QtCore.Qt.Key_Plus or event.key() == QtCore.Qt.Key_Equal:
            self.zoom_in()
        elif event.key() == QtCore.Qt.Key_Minus:
            self.zoom_out()
        elif event.key() == QtCore.Qt.Key_0:
            self.reset_zoom()
        elif event.key() == QtCore.Qt.Key_F:
            self.fit_to_window()
        elif event.key() == QtCore.Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event) 