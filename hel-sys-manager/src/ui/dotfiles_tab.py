import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton, QHBoxLayout, QMessageBox, QFileDialog, QInputDialog
from PyQt5.QtCore import Qt
import os
from src.core.dotfiles_handler import DotfilesHandler

# حذف أسطر الطباعة الخاصة بالتشخيص
# print("--- dotfiles_tab.py context ---")
# print(f"CWD: {os.getcwd()}")
# print(f"sys.path: {sys.path}")
# print("-------------------------------")

class DotfilesTab(QWidget):
    def __init__(self):
        super().__init__()
        self.handler = DotfilesHandler()
        self._setup_ui()
        self._load_dotfiles()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        title_label = QLabel("Manage Your Dotfiles")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(title_label)
        desc_label = QLabel("Here you can view, manage, and back up your personal configuration files (dotfiles).")
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet("font-size: 14px; margin-bottom: 20px;")
        main_layout.addWidget(desc_label)
        self.dotfiles_list_widget = QListWidget()
        self.dotfiles_list_widget.setSelectionMode(QListWidget.ExtendedSelection) # <-- تغيير هنا: السماح بتحديد عناصر متعددة
        main_layout.addWidget(self.dotfiles_list_widget)
        
        buttons_layout = QHBoxLayout()
        
        self.refresh_button = QPushButton("Refresh List")
        self.refresh_button.clicked.connect(self._load_dotfiles)
        buttons_layout.addWidget(self.refresh_button)
        
        self.view_button = QPushButton("View/Edit Selected")
        self.view_button.setEnabled(False) 
        buttons_layout.addWidget(self.view_button)

        self.create_symlink_button = QPushButton("Create Symlink")
        self.create_symlink_button.clicked.connect(self._create_symlink)
        buttons_layout.addWidget(self.create_symlink_button)

        # أزرار النسخ الاحتياطي والاستعادة الجديدة
        # New Backup and Restore Buttons
        self.backup_button = QPushButton("Backup Selected")
        self.backup_button.setEnabled(False) # سيعتمد على تحديد العنصر
        self.backup_button.clicked.connect(self._backup_selected_dotfiles) # ربط الزر بالدالة الجديدة
        buttons_layout.addWidget(self.backup_button)

        self.restore_button = QPushButton("Restore Dotfiles")
        self.restore_button.clicked.connect(self._restore_dotfiles) # ربط الزر بالدالة الجديدة
        buttons_layout.addWidget(self.restore_button)
        
        main_layout.addLayout(buttons_layout)
        
        self.dotfiles_list_widget.itemSelectionChanged.connect(self._on_selection_changed)
    
    def _load_dotfiles(self):
        self.dotfiles_list_widget.clear()
        dotfiles = self.handler.get_dotfiles_in_home()
        if dotfiles:
            self.dotfiles_list_widget.addItems(dotfiles)
        else:
            self.dotfiles_list_widget.addItem("No dotfiles found in your home directory.")
        self._on_selection_changed()

    def _on_selection_changed(self):
        # تمكين/تعطيل الأزرار بناءً على ما إذا كان هناك عنصر واحد على الأقل محدد
        # Enable/disable buttons based on whether at least one item is selected
        has_selection = bool(self.dotfiles_list_widget.selectedItems())
        self.view_button.setEnabled(has_selection)
        self.backup_button.setEnabled(has_selection)
        # زر create_symlink_button و restore_button لا يعتمدان على تحديد عنصر في القائمة
        
    def _create_symlink(self):
        source_file, _ = QFileDialog.getOpenFileName(self, "Select Source Dotfile", os.path.expanduser("~"), "All Files (*);;Dotfiles (.*)")
        
        if not source_file: 
            return

        default_link_name = os.path.basename(source_file)
        if not default_link_name.startswith('.'):
            default_link_name = '.' + default_link_name
            
        link_name, ok = QInputDialog.getText(self, "Create Symbolic Link", 
                                             f"Enter the name for the symlink in your home directory:\n(Source: {source_file})",
                                             text=default_link_name)
        
        if not ok or not link_name:
            return

        target_link_path = os.path.join(os.path.expanduser("~"), link_name)

        reply = QMessageBox.question(self, 'Confirm Symlink Creation', 
                                    f"Are you sure you want to create a symbolic link?\n\nSource: {source_file}\nTarget: {target_link_path}",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            success, message = self.handler.create_symlink(source_file, target_link_path)
            if success:
                QMessageBox.information(self, "Symlink Created", message)
                self._load_dotfiles()
            else:
                QMessageBox.critical(self, "Symlink Error", message)

    # دالة جديدة للنسخ الاحتياطي للملفات المحددة
    # New function for backing up selected dotfiles
    def _backup_selected_dotfiles(self):
        selected_dotfiles = [item.text() for item in self.dotfiles_list_widget.selectedItems()]
        
        if not selected_dotfiles:
            QMessageBox.warning(self, "No Dotfiles Selected", "Please select at least one dotfile to backup.")
            return

        # السماح للمستخدم باختيار دليل لحفظ النسخة الاحتياطية
        backup_dir = QFileDialog.getExistingDirectory(self, "Select Backup Directory", os.path.expanduser("~"))

        if not backup_dir: # إذا ألغى المستخدم
            return

        reply = QMessageBox.question(self, 'Confirm Backup', 
                                    f"Are you sure you want to backup the selected dotfiles to:\n'{backup_dir}'?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            success, message = self.handler.backup_dotfiles(selected_dotfiles, backup_dir)
            if success:
                QMessageBox.information(self, "Backup Complete", message)
            else:
                QMessageBox.critical(self, "Backup Error", message)

    # دالة جديدة لاستعادة ملفات الـ Dotfiles
    # New function for restoring dotfiles
    def _restore_dotfiles(self):
        # السماح للمستخدم باختيار دليل يحتوي على ملفات Dotfiles للنسخ الاحتياطي
        source_dir = QFileDialog.getExistingDirectory(self, "Select Source Directory for Restore", os.path.expanduser("~"))

        if not source_dir: # إذا ألغى المستخدم
            return

        reply = QMessageBox.question(self, 'Confirm Restore', 
                                    f"Are you sure you want to restore dotfiles from:\n'{source_dir}'\n\nThis might overwrite existing dotfiles in your home directory.",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            # هنا سنحتاج لتحديد ما إذا كنا سنستعيد كل الملفات في المجلد
            # أو فقط ملفات معينة. حالياً، لنفترض أننا سنستعيد كل ملفات الـ Dotfiles الموجودة في source_dir.
            success, message = self.handler.restore_dotfiles(source_dir, os.path.expanduser("~")) # استعادة إلى دليل المنزل
            if success:
                QMessageBox.information(self, "Restore Complete", message)
                self._load_dotfiles() # تحديث القائمة بعد الاستعادة
            else:
                QMessageBox.critical(self, "Restore Error", message)
