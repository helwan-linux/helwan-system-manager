import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton, QHBoxLayout, QMessageBox, QFileDialog, QInputDialog
from PyQt5.QtCore import Qt
import os
from src.core.dotfiles_handler import DotfilesHandler


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
        self.dotfiles_list_widget.setSelectionMode(QListWidget.SingleSelection)
        main_layout.addWidget(self.dotfiles_list_widget)
        buttons_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh List")
        self.refresh_button.clicked.connect(self._load_dotfiles)
        buttons_layout.addWidget(self.refresh_button)
        self.view_button = QPushButton("View/Edit Selected")
        self.view_button.setEnabled(False)
        buttons_layout.addWidget(self.view_button)

        # زر إنشاء الرابط الرمزي الجديد (تعديل هذا الجزء)
        # New Create Symlink Button (modify this part)
        self.create_symlink_button = QPushButton("Create Symlink")
        self.create_symlink_button.clicked.connect(self._create_symlink) # ربط الزر بالدالة الجديدة
        buttons_layout.addWidget(self.create_symlink_button) # تم تغيير هذا السطر

        self.backup_button = QPushButton("Backup Selected")
        self.backup_button.setEnabled(False)
        buttons_layout.addWidget(self.backup_button)
        main_layout.addLayout(buttons_layout)
        self.dotfiles_list_widget.itemSelectionChanged.connect(self._on_selection_changed)
        
        # لا نحتاج لتمكين / تعطيل زر create_symlink_button بناءً على التحديد
        # لأنه يعمل على ملفات غير موجودة في القائمة
        self.symlink_button = None # حذف السطر القديم
    
    def _load_dotfiles(self):
        self.dotfiles_list_widget.clear()
        dotfiles = self.handler.get_dotfiles_in_home()
        if dotfiles:
            self.dotfiles_list_widget.addItems(dotfiles)
        else:
            self.dotfiles_list_widget.addItem("No dotfiles found in your home directory.")
        self._on_selection_changed()

    def _on_selection_changed(self):
        has_selection = self.dotfiles_list_widget.currentItem() is not None
        self.view_button.setEnabled(has_selection)
        # self.symlink_button.setEnabled(has_selection) # حذف هذا السطر
        self.backup_button.setEnabled(has_selection)

    # دالة جديدة لإنشاء الرابط الرمزي
    # New function for creating a symbolic link
    def _create_symlink(self):
        # 1. اختيار الملف المصدر (الذي سيتم الربط إليه)
        source_file, _ = QFileDialog.getOpenFileName(self, "Select Source Dotfile", os.path.expanduser("~"), "All Files (*);;Dotfiles (.*)")
        
        if not source_file: # إذا لم يختر المستخدم ملفًا
            return

        # 2. تحديد اسم الرابط الرمزي الافتراضي (غالباً نفس اسم الملف المصدر)
        default_link_name = os.path.basename(source_file)
        # التأكد أن الاسم يبدأ بنقطة إذا لم يكن كذلك
        if not default_link_name.startswith('.'):
            default_link_name = '.' + default_link_name
            
        # 3. سؤال المستخدم عن اسم الرابط الرمزي المستهدف في دليل المنزل
        link_name, ok = QInputDialog.getText(self, "Create Symbolic Link", 
                                             f"Enter the name for the symlink in your home directory:\n(Source: {source_file})",
                                             text=default_link_name)
        
        if not ok or not link_name: # إذا ألغى المستخدم أو أدخل اسماً فارغاً
            return

        # 4. تحديد المسار الكامل للرابط الرمزي المستهدف (في دليل المنزل)
        target_link_path = os.path.join(os.path.expanduser("~"), link_name)

        # 5. تأكيد من المستخدم
        reply = QMessageBox.question(self, 'Confirm Symlink Creation', 
                                    f"Are you sure you want to create a symbolic link?\n\nSource: {source_file}\nTarget: {target_link_path}",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            # استدعاء الدالة في DotfilesHandler لإنشاء الرابط
            success, message = self.handler.create_symlink(source_file, target_link_path)
            if success:
                QMessageBox.information(self, "Symlink Created", message)
                self._load_dotfiles() # تحديث القائمة بعد الإنشاء
            else:
                QMessageBox.critical(self, "Symlink Error", message)
