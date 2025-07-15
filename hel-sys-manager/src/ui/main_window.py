from PyQt5.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QWidget, QAction, QMenu, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import os

# Import project tabs using relative imports
from .system_tab import SystemTab
from .services_tab import ServicesTab
from .packages_tab import PackagesTab
from .dotfiles_tab import DotfilesTab
from .about_dialog import AboutDialog 
from .help_dialog import HelpDialog # Import the new help dialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hel System Manager") # Changed title to English for consistency

        # Set application icon: path is relative to main_window.py's location
        # (.. goes out of ui to src, then goes to assets/icons)
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', 'assets', 'icons', 'app_icon.png')))

        self.setGeometry(100, 100, 1000, 700) 

        self._load_tab_icons() 
        self._create_tabs()
        self._create_menu_bar()

    def _load_tab_icons(self):
        # Path is relative to the src directory (where main_window.py is now located in src/ui, so .. gets to src, then .. to project root if assets are there, assuming assets is in src for now based on previous info or needs adjustment)
        # Assuming assets/icons is directly under src, so `../assets/icons` is correct if this file is in src/ui
        base_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'icons')
        
        self.system_icon = QIcon(os.path.join(base_path, 'system.png'))
        self.services_icon = QIcon(os.path.join(base_path, 'services.png'))
        self.packages_icon = QIcon(os.path.join(base_path, 'packages.png'))
        self.dotfiles_icon = QIcon(os.path.join(base_path, 'dotfiles.png'))

    def _create_tabs(self):
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        self.tab_widget.addTab(SystemTab(), self.system_icon, "System")
        self.tab_widget.addTab(ServicesTab(), self.services_icon, "Services")
        self.tab_widget.addTab(PackagesTab(), self.packages_icon, "Packages")
        self.tab_widget.addTab(DotfilesTab(), self.dotfiles_icon, "Dotfiles")

    def _create_menu_bar(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About Hel System Manager", self) # Changed text to English
        about_action.triggered.connect(self._show_about_dialog)
        help_menu.addAction(about_action)

        help_action = QAction("Documentation", self) # Changed text to English
        help_action.triggered.connect(self._show_help_dialog)
        help_menu.addAction(help_action)

    def _show_about_dialog(self):
        """
        Shows an about dialog for the application.
        """
        about_dialog = AboutDialog(self)
        about_dialog.exec_()

    def _show_help_dialog(self):
        """
        Shows a help dialog about the program.
        """
        # Create and show the custom help dialog
        help_dialog = HelpDialog(self)
        help_dialog.exec_() # Show the dialog modally
