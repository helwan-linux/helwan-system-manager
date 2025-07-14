from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QDialog, QTextEdit, QDialogButtonBox
)
from PyQt5.QtCore import Qt
from src.core.pacman_aur_manager import PacmanAURManager


class PackagesTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        # شريط البحث وأزرار التحديث
        self.top_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search for packages...")
        self.search_input.returnPressed.connect(self._search_packages)
        self.top_layout.addWidget(self.search_input)

        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self._search_packages)
        self.top_layout.addWidget(self.search_button)

        self.update_system_button = QPushButton("Update System")
        self.update_system_button.clicked.connect(self._update_system)
        self.top_layout.addWidget(self.update_system_button)

        self.layout.addLayout(self.top_layout)

        # جدول عرض الحزم
        self.packages_table = QTableWidget()
        self.packages_table.setColumnCount(4)
        self.packages_table.setHorizontalHeaderLabels(["Repo", "Name", "Version", "Description"])
        self.packages_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.packages_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.packages_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.packages_table.itemSelectionChanged.connect(self._update_action_buttons_state)
        self.packages_table.doubleClicked.connect(self._show_package_info)

        self.layout.addWidget(self.packages_table)

        # أزرار الإجراءات
        self.action_buttons_layout = QHBoxLayout()
        self.install_button = QPushButton("Install")
        self.remove_button = QPushButton("Remove")
        self.info_button = QPushButton("Info")

        self.install_button.clicked.connect(lambda: self._perform_package_action("install"))
        self.remove_button.clicked.connect(lambda: self._perform_package_action("remove"))
        self.info_button.clicked.connect(self._show_package_info)

        self.action_buttons_layout.addWidget(self.install_button)
        self.action_buttons_layout.addWidget(self.remove_button)
        self.action_buttons_layout.addWidget(self.info_button)
        self.layout.addLayout(self.action_buttons_layout)

        self._update_action_buttons_state()

    def _search_packages(self):
        query = self.search_input.text().strip()
        if not query:
            QMessageBox.warning(self, "Search Query Empty", "Please enter a package name to search.")
            self.packages_table.setRowCount(0)
            return

        self.packages_table.setRowCount(0)
        self.packages_table.setColumnCount(4)
        self.packages_table.setHorizontalHeaderLabels(["Repo", "Name", "Version", "Description"])

        self.all_found_packages = PacmanAURManager.search_packages(query)
        self._display_packages(self.all_found_packages)

    def _display_packages(self, packages):
        self.packages_table.setRowCount(len(packages))
        for row, pkg in enumerate(packages):
            self.packages_table.setItem(row, 0, QTableWidgetItem(pkg.get("repo", "N/A")))
            self.packages_table.setItem(row, 1, QTableWidgetItem(pkg.get("name", "N/A")))
            self.packages_table.setItem(row, 2, QTableWidgetItem(pkg.get("version", "N/A")))
            self.packages_table.setItem(row, 3, QTableWidgetItem(pkg.get("description", "N/A")))
        self._update_action_buttons_state()

    def _update_action_buttons_state(self):
        is_selected = len(self.packages_table.selectedItems()) > 0
        self.install_button.setEnabled(is_selected)
        self.remove_button.setEnabled(is_selected)
        self.info_button.setEnabled(is_selected)

    def _perform_package_action(self, action):
        selected_items = self.packages_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Package Selected", "Please select a package.")
            return

        package_name = selected_items[1].text()  # ← هذا هو العمود الصحيح لاسم الحزمة

        reply = QMessageBox.question(self, f"Confirm {action.capitalize()}",
                                     f"Are you sure you want to {action} package: {package_name}?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            result = ""
            if action == "install":
                result = PacmanAURManager.install_package(package_name)
            elif action == "remove":
                result = PacmanAURManager.remove_package(package_name)

            if result.startswith("Error:"):
                QMessageBox.critical(self, f"{action.capitalize()} Failed", result)
            else:
                QMessageBox.information(self, f"{action.capitalize()} Successful",
                                        f"Package '{package_name}' {action}ed successfully.")
                self._search_packages()

    def _show_package_info(self):
        selected_items = self.packages_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Package Selected", "Please select a package to view info.")
            return

        package_name = selected_items[1].text()  # ← اسم الحزمة من العمود الصحيح

        info_dialog = QDialog(self)
        info_dialog.setWindowTitle(f"Package Info: {package_name}")
        info_dialog.setMinimumSize(600, 400)
        dialog_layout = QVBoxLayout(info_dialog)

        info_text_edit = QTextEdit()
        info_text_edit.setReadOnly(True)
        dialog_layout.addWidget(info_text_edit)

        info = PacmanAURManager.get_package_info(package_name)
        if "Error" in info:
            info_text_edit.setText(f"Error: {info['Error']}")
        else:
            formatted = ""
            for k, v in info.items():
                formatted += f"<b>{k}:</b> {v}\n"
            info_text_edit.setHtml(formatted)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(info_dialog.accept)
        dialog_layout.addWidget(button_box)

        info_dialog.exec_()

    def _update_system(self):
        reply = QMessageBox.question(self, "System Update",
                                     "Are you sure you want to update the system?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            QMessageBox.information(self, "System Update", "Starting system update...")
            result = PacmanAURManager.update_system()
            if result.startswith("Error:"):
                QMessageBox.critical(self, "Update Failed", result)
            else:
                QMessageBox.information(self, "Update Complete", "System updated successfully.")
