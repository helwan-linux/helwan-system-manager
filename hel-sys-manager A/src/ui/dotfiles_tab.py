from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt
import os
from src.core.dotfiles_handler import DotfilesHandler # <--- هذا هو التغيير الأساسي: المسار الصحيح

class DotfilesTab(QWidget):
    def __init__(self):
        """
        Initializes the Dotfiles Management tab.
        """
        super().__init__()
        self.handler = DotfilesHandler() # Initialize the handler

        self._setup_ui()
        self._load_dotfiles() # Load dotfiles on startup

    def _setup_ui(self):
        """
        Sets up the UI elements for the Dotfiles tab.
        """
        main_layout = QVBoxLayout(self)

        # Title Label
        title_label = QLabel("Manage Your Dotfiles")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(title_label)

        # Description Label
        desc_label = QLabel("Here you can view, manage, and back up your personal configuration files (dotfiles).")
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet("font-size: 14px; margin-bottom: 20px;")
        main_layout.addWidget(desc_label)

        # List Widget for Dotfiles
        self.dotfiles_list_widget = QListWidget()
        self.dotfiles_list_widget.setSelectionMode(QListWidget.SingleSelection)
        main_layout.addWidget(self.dotfiles_list_widget)

        # Buttons Layout
        buttons_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh List")
        self.refresh_button.clicked.connect(self._load_dotfiles)
        buttons_layout.addWidget(self.refresh_button)

        # Placeholder for future buttons
        self.view_button = QPushButton("View/Edit Selected")
        self.view_button.setEnabled(False) # Initially disabled
        buttons_layout.addWidget(self.view_button)

        self.symlink_button = QPushButton("Create Symlink")
        self.symlink_button.setEnabled(False) # Initially disabled
        buttons_layout.addWidget(self.symlink_button)

        self.backup_button = QPushButton("Backup Selected")
        self.backup_button.setEnabled(False) # Initially disabled
        buttons_layout.addWidget(self.backup_button)

        main_layout.addLayout(buttons_layout)

        # Connect selection change to enable/disable buttons
        self.dotfiles_list_widget.itemSelectionChanged.connect(self._on_selection_changed)

    def _load_dotfiles(self):
        """
        Loads dotfiles from the home directory and populates the QListWidget.
        """
        self.dotfiles_list_widget.clear() # Clear existing items
        dotfiles = self.handler.get_dotfiles_in_home()
        if dotfiles:
            self.dotfiles_list_widget.addItems(dotfiles)
        else:
            self.dotfiles_list_widget.addItem("No dotfiles found in your home directory.")
        self._on_selection_changed() # Update button states after loading

    def _on_selection_changed(self):
        """
        Enables/disables buttons based on item selection in the list.
        """
        has_selection = self.dotfiles_list_widget.currentItem() is not None
        self.view_button.setEnabled(has_selection)
        self.symlink_button.setEnabled(has_selection)
        self.backup_button.setEnabled(has_selection)
