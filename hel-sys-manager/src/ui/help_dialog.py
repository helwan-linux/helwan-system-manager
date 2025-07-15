from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextBrowser, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt, QDir
import os

class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Help - Hel System Manager") # تم التغيير إلى الإنجليزية
        self.setMinimumSize(700, 500) # Set a default size for the window

        self.layout = QVBoxLayout(self)

        self.text_browser = QTextBrowser(self)
        self.text_browser.setOpenExternalLinks(True) # To open external links in the default browser
        self.layout.addWidget(self.text_browser)

        # Add a close button
        self.button_layout = QHBoxLayout()
        self.close_button = QPushButton("Close") # تم التغيير إلى الإنجليزية
        self.close_button.clicked.connect(self.accept) # On close button click, close the window
        self.button_layout.addStretch() # To push the button to the right
        self.button_layout.addWidget(self.close_button)
        self.layout.addLayout(self.button_layout)

        self._load_help_content() # Load content on initialization

    def _load_help_content(self):
        # Define the path to the documentation file
        # Assume the docs folder is in the main project directory
        # This directory is the parent of the src folder
        current_script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.join(current_script_dir, "..", "..") # To go from src/ui/ to root
        
        help_file_path = os.path.join(project_root, "docs", "help.md")

        if os.path.exists(help_file_path):
            try:
                with open(help_file_path, "r", encoding="utf-8") as f:
                    markdown_content = f.read()
                
                self.text_browser.setMarkdown(markdown_content) # QTextBrowser supports Markdown directly! (PyQt 5.14+)
                
            except Exception as e:
                self.text_browser.setText(f"Error loading help content: {e}")
        else:
            self.text_browser.setText("<h1>Error: Help documentation file not found.</h1><p>Please ensure 'docs/help.md' exists in the project root directory.</p>")
