import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QListWidget, QTextEdit, QMessageBox, QDialog
from PyQt5.QtCore import Qt
import os
from src.core.package_handler import PackageHandler

class PackagesTab(QWidget):
    def __init__(self):
        super().__init__()
        self.handler = PackageHandler()
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        title_label = QLabel("Package Management")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(title_label)

        # قسم البحث عن الحزم
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search for packages...")
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self._search_packages)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        main_layout.addLayout(search_layout)

        # قائمة نتائج البحث/الحزم المثبتة
        self.package_list_widget = QListWidget()
        self.package_list_widget.setSelectionMode(QListWidget.SingleSelection)
        self.package_list_widget.itemSelectionChanged.connect(self._on_package_selection_changed)
        main_layout.addWidget(self.package_list_widget)

        # عرض تفاصيل الحزمة المحددة
        self.package_details_label = QLabel("Package Details:")
        main_layout.addWidget(self.package_details_label)
        self.package_details_text = QTextEdit()
        self.package_details_text.setReadOnly(True)
        main_layout.addWidget(self.package_details_text)

        # أزرار الميزات الأخرى (تثبيت، إزالة، تحديث، سجل، إدارة المستودعات، قائمة المثبتة)
        bottom_buttons_layout = QHBoxLayout()
        
        # زر جديد
        self.list_installed_button = QPushButton("List Installed")
        self.list_installed_button.clicked.connect(self._list_installed_packages)
        bottom_buttons_layout.addWidget(self.list_installed_button)

        self.install_button = QPushButton("Install Selected")
        self.install_button.setEnabled(False) # تعطيل حتى يتم تحديد حزمة
        self.install_button.clicked.connect(self._install_selected_package)
        bottom_buttons_layout.addWidget(self.install_button)

        self.remove_button = QPushButton("Remove Selected")
        self.remove_button.setEnabled(False) # تعطيل حتى يتم تحديد حزمة
        self.remove_button.clicked.connect(self._remove_selected_package)
        bottom_buttons_layout.addWidget(self.remove_button)

        self.update_button = QPushButton("Update System")
        self.update_button.clicked.connect(self._update_system)
        bottom_buttons_layout.addWidget(self.update_button)

        self.show_history_button = QPushButton("Show History")
        self.show_history_button.clicked.connect(self._show_package_history)
        bottom_buttons_layout.addWidget(self.show_history_button)

        self.manage_repos_button = QPushButton("Manage Repositories")
        self.manage_repos_button.clicked.connect(self._manage_repositories)
        bottom_buttons_layout.addWidget(self.manage_repos_button)

        main_layout.addLayout(bottom_buttons_layout)
        
        # عند التهيئة، قم بتحديث حالة الأزرار بناءً على ما إذا كانت هناك حزمة محددة
        # self._on_package_selection_changed() # لا تقم باستدعاء هذه الدالة هنا، لأنها ستفشل

    def _on_package_selection_changed(self):
        # **تأكد من أن هذا السطر هو الأول في الدالة**
        selected_items = self.package_list_widget.selectedItems() 
        
        # تمكين/تعطيل أزرار التثبيت والإزالة بناءً على تحديد عنصر في القائمة
        has_selection = bool(selected_items)
        self.install_button.setEnabled(has_selection)
        self.remove_button.setEnabled(has_selection)

        if not selected_items:
            self.package_details_text.clear()
            return

        selected_package_name = selected_items[0].text()
        
        success, details = self.handler.get_package_details(selected_package_name)
        if success:
            self.package_details_text.setText(details)
        else:
            self.package_details_text.setText(f"Could not retrieve details: {details}")
            QMessageBox.critical(self, "Details Error", details)

    def _search_packages(self):
        query = self.search_input.text().strip()
        if not query:
            QMessageBox.warning(self, "Search Error", "Please enter a package name to search.")
            return

        self.package_list_widget.clear()
        self.package_details_text.clear()

        success, result = self.handler.search_packages(query)
        if success:
            if isinstance(result, list): # نتوقع قائمة من أسماء الحزم
                if result:
                    self.package_list_widget.addItems(result)
                else:
                    self.package_list_widget.addItem(f"No packages found for '{query}'.")
            else: # إذا كانت النتيجة رسالة خطأ
                QMessageBox.critical(self, "Search Error", result)
        else:
            QMessageBox.critical(self, "Search Error", result)
        
        self._on_package_selection_changed() # استدعاء هنا لتحديث حالة الأزرار بعد البحث

    # دالة جديدة لعرض الحزم المثبتة
    def _list_installed_packages(self):
        self.package_list_widget.clear()
        self.package_details_text.clear()

        success, result = self.handler.list_installed_packages()
        if success:
            if isinstance(result, list):
                if result:
                    self.package_list_widget.addItems(result)
                else:
                    self.package_list_widget.addItem("No installed packages found.")
            else:
                QMessageBox.critical(self, "List Installed Error", result)
        else:
            QMessageBox.critical(self, "List Installed Error", result)
        
        self._on_package_selection_changed() # استدعاء هنا لتحديث حالة الأزرار بعد العرض


    def _install_selected_package(self):
        selected_items = self.package_list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Package Selected", "Please select a package to install.")
            return

        package_name = selected_items[0].text()
        reply = QMessageBox.question(self, 'Confirm Installation', 
                                    f"Are you sure you want to install '{package_name}'?\n\nThis may require root privileges.",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            QMessageBox.information(self, "Installation", "Please authorize the root privileges in the terminal/popup if prompted.")
            success, message = self.handler.install_package(package_name)
            if success:
                self._show_scrollable_message("Installation Complete", message) # تم التعديل هنا
                # ربما نحدث قائمة الحزم المثبتة هنا لاحقاً
            else:
                QMessageBox.critical(self, "Installation Error", message)

    def _remove_selected_package(self):
        selected_items = self.package_list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Package Selected", "Please select a package to remove.")
            return

        package_name = selected_items[0].text()
        reply = QMessageBox.question(self, 'Confirm Removal', 
                                    f"Are you sure you want to remove '{package_name}'?\n\nThis may require root privileges.",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            QMessageBox.information(self, "Removal", "Please authorize the root privileges in the terminal/popup if prompted.")
            success, message = self.handler.remove_package(package_name)
            if success:
                self._show_scrollable_message("Removal Complete", message) # تم التعديل هنا
                # ربما نحدث قائمة الحزم المثبتة هنا لاحقاً
            else:
                QMessageBox.critical(self, "Removal Error", message)

    def _update_system(self):
        reply = QMessageBox.question(self, 'Confirm System Update', 
                                    "Are you sure you want to update the entire system?\n\nThis will update all installed packages and may take some time. Requires root privileges.",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            QMessageBox.information(self, "System Update", "Please authorize the root privileges in the terminal/popup if prompted.")
            success, message = self.handler.update_system()
            if success:
                self._show_scrollable_message("System Update Complete", message) # تم التعديل هنا
            else:
                QMessageBox.critical(self, "System Update Error", message)

    def _show_package_history(self):
        success, history_content = self.handler.get_package_history()
        if success:
            history_dialog = QMessageBox()
            history_dialog.setWindowTitle("Package History")
            history_dialog.setText("Recent Package History:")
            history_dialog.setInformativeText(history_content)
            history_dialog.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
            history_dialog.setStandardButtons(QMessageBox.Ok)
            history_dialog.exec_()
        else:
            QMessageBox.critical(self, "History Error", history_content)

    def _manage_repositories(self):
        QMessageBox.information(self, "Manage Repositories", "This feature will allow adding/removing/editing package repositories. (Advanced - To be implemented)")

    def _show_scrollable_message(self, title, message):
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setMinimumSize(400, 300) # تحديد حجم افتراضي للنافذة
        
        layout = QVBoxLayout(dialog)
        
        text_edit = QTextEdit(dialog)
        text_edit.setReadOnly(True)
        text_edit.setText(message)
        layout.addWidget(text_edit)
        
        ok_button = QPushButton("OK", dialog)
        ok_button.clicked.connect(dialog.accept)
        layout.addWidget(ok_button)
        
        dialog.exec_()
