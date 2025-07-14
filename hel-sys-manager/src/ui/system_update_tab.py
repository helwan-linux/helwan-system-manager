from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QLineEdit, QMessageBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from src.core.system_utils import SystemUtils


class UpdateWorker(QThread):
    output_ready = pyqtSignal(str)

    def run(self):
        result = SystemUtils.run_pacman_update()
        self.output_ready.emit(result)


class InstallWorker(QThread):
    output_ready = pyqtSignal(str)

    def __init__(self, packages):
        super().__init__()
        self.packages = packages

    def run(self):
        result = SystemUtils.install_packages(self.packages)
        self.output_ready.emit(result)


class SystemUpdateTab(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.update_info_label = QLabel("Fetching update info...")
        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)

        self.update_button = QPushButton("Update System")
        self.install_input = QLineEdit()
        self.install_input.setPlaceholderText("Enter package names separated by space...")
        self.install_button = QPushButton("Install Packages")

        layout.addWidget(self.update_info_label)
        layout.addWidget(self.update_button)
        layout.addWidget(QLabel("Installation:"))
        layout.addWidget(self.install_input)
        layout.addWidget(self.install_button)
        layout.addWidget(QLabel("Output:"))
        layout.addWidget(self.output_box)

        self.setLayout(layout)

        self.update_button.clicked.connect(self.perform_update)
        self.install_button.clicked.connect(self.perform_install)

        self.load_update_info()

    def load_update_info(self):
        stats = SystemUtils.get_pacman_stats()
        self.update_info_label.setText(
            f"Installed packages: {stats['total']} | Updates available: {stats['updates_count']}"
        )
        if stats['updates_count'] > 0:
            self.output_box.setPlainText("\n".join(stats['updates']))
        else:
            self.output_box.setPlainText("System is up to date.")

    def perform_update(self):
        self.output_box.setPlainText("Updating system...")
        self.update_thread = UpdateWorker()
        self.update_thread.output_ready.connect(self.output_box.setPlainText)
        self.update_thread.start()

    def perform_install(self):
        packages = self.install_input.text().strip().split()
        if not packages:
            QMessageBox.warning(self, "Error", "Please enter package names.")
            return

        self.output_box.setPlainText(f"Installing: {' '.join(packages)}")
        self.install_thread = InstallWorker(packages)
        self.install_thread.output_ready.connect(self.output_box.setPlainText)
        self.install_thread.start()
