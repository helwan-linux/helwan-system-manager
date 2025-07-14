from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QScrollArea
)
from PyQt5.QtCore import Qt, QTimer
from src.core.services_manager import ServicesManager # استيراد الكلاس الجديد

class ServicesTab(QWidget):
    def __init__(self):
        """
        تهيئة تبويبة إدارة خدمات systemd.
        Initializes the systemd Services Management tab.
        """
        super().__init__()
        self.layout = QVBoxLayout(self)

        # شريط البحث
        # Search bar
        self.search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search for services...")
        self.search_input.textChanged.connect(self._filter_services)
        self.search_layout.addWidget(self.search_input)

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self._load_services)
        self.search_layout.addWidget(self.refresh_button)
        self.layout.addLayout(self.search_layout)

        # جدول الخدمات
        # Services table
        self.services_table = QTableWidget()
        self.services_table.setColumnCount(5)
        self.services_table.setHorizontalHeaderLabels(["Name", "Load", "Active", "Sub", "Description"])
        self.services_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # توزيع الأعمدة بالتساوي
        self.services_table.setSelectionBehavior(QTableWidget.SelectRows) # تحديد الصف بأكمله
        self.services_table.setEditTriggers(QTableWidget.NoEditTriggers) # منع التعديل المباشر في الجدول
        self.services_table.itemSelectionChanged.connect(self._update_action_buttons_state) # تحديث حالة الأزرار

        self.layout.addWidget(self.services_table)

        # أزرار الإجراءات
        # Action buttons
        self.action_buttons_layout = QHBoxLayout()
        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.restart_button = QPushButton("Restart")
        self.enable_button = QPushButton("Enable")
        self.disable_button = QPushButton("Disable")

        self.start_button.clicked.connect(lambda: self._perform_service_action("start"))
        self.stop_button.clicked.connect(lambda: self._perform_service_action("stop"))
        self.restart_button.clicked.connect(lambda: self._perform_service_action("restart"))
        self.enable_button.clicked.connect(lambda: self._perform_service_action("enable"))
        self.disable_button.clicked.connect(lambda: self._perform_service_action("disable"))

        self.action_buttons_layout.addWidget(self.start_button)
        self.action_buttons_layout.addWidget(self.stop_button)
        self.action_buttons_layout.addWidget(self.restart_button)
        self.action_buttons_layout.addWidget(self.enable_button)
        self.action_buttons_layout.addWidget(self.disable_button)
        self.layout.addLayout(self.action_buttons_layout)

        self._update_action_buttons_state() # تعطيل الأزرار في البداية
        self._load_services() # تحميل الخدمات عند بدء التبويبة
        
        # مؤقت للتحديث التلقائي (اختياري، يمكن إزالته إذا كان الحمل على النظام كبيراً)
        # Auto-refresh timer (optional, can be removed if system load is high)
        self.refresh_timer = QTimer(self)
        self.refresh_timer.setInterval(10000) # تحديث كل 10 ثوانٍ
        self.refresh_timer.timeout.connect(self._load_services)
        self.refresh_timer.start()

    def _load_services(self):
        """
        جلب وعرض قائمة الخدمات في الجدول.
        Fetches and displays the list of services in the table.
        """
        self.all_services = ServicesManager.list_services()
        self._filter_services(self.search_input.text()) # إعادة تصفية الخدمات بعد التحميل

    def _filter_services(self, text):
        """
        تصفية الخدمات المعروضة بناءً على نص البحث.
        Filters displayed services based on search text.
        """
        filtered_services = [
            s for s in self.all_services
            if text.lower() in s["name"].lower() or text.lower() in s["description"].lower()
        ]
        self._display_services(filtered_services)

    def _display_services(self, services):
        """
        عرض الخدمات في جدول QTableWidget.
        Displays services in the QTableWidget.
        """
        self.services_table.setRowCount(len(services))
        for row, service in enumerate(services):
            self.services_table.setItem(row, 0, QTableWidgetItem(service["name"]))
            self.services_table.setItem(row, 1, QTableWidgetItem(service["load"]))
            self.services_table.setItem(row, 2, QTableWidgetItem(service["active"]))
            self.services_table.setItem(row, 3, QTableWidgetItem(service["sub"]))
            self.services_table.setItem(row, 4, QTableWidgetItem(service["description"]))
        self._update_action_buttons_state() # تحديث حالة الأزرار بعد التحديث

    def _update_action_buttons_state(self):
        """
        تحديث حالة أزرار الإجراءات (تمكين/تعطيل) بناءً على تحديد الصفوف.
        Updates the state of action buttons (enable/disable) based on row selection.
        """
        is_selected = len(self.services_table.selectedItems()) > 0
        self.start_button.setEnabled(is_selected)
        self.stop_button.setEnabled(is_selected)
        self.restart_button.setEnabled(is_selected)
        self.enable_button.setEnabled(is_selected)
        self.disable_button.setEnabled(is_selected)

    def _perform_service_action(self, action):
        """
        تنفيذ الإجراء المطلوب على الخدمة المحددة.
        Performs the requested action on the selected service.
        """
        selected_items = self.services_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Service Selected", "Please select a service to perform this action.")
            return

        # اسم الخدمة هو في العمود الأول (index 0) من الصف المحدد
        # The service name is in the first column (index 0) of the selected row
        service_name = selected_items[0].text()

        reply = QMessageBox.question(self, f"Confirm {action.capitalize()}",
                                     f"Are you sure you want to {action} service: <b>{service_name}</b>?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            result = ""
            if action == "start":
                result = ServicesManager.start_service(service_name)
            elif action == "stop":
                result = ServicesManager.stop_service(service_name)
            elif action == "restart":
                result = ServicesManager.restart_service(service_name)
            elif action == "enable":
                result = ServicesManager.enable_service(service_name)
            elif action == "disable":
                result = ServicesManager.disable_service(service_name)
            
            if result.startswith("Error:"):
                QMessageBox.critical(self, f"{action.capitalize()} Failed", result)
            else:
                QMessageBox.information(self, f"{action.capitalize()} Successful", f"Service '{service_name}' {action}ed successfully.")
                self._load_services() # إعادة تحميل الخدمات لتحديث الحالة
