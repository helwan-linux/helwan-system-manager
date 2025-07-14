from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, QProgressBar, QScrollArea
from PyQt5.QtCore import Qt, QTimer
from src.core.system_utils import SystemUtils # استيراد الكلاس المساعد

class SystemTab(QWidget):
    def __init__(self):
        """
        تهيئة تبويبة معلومات وإدارة النظام.
        Initializes the System Information and Management tab.
        """
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.scroll_area = QScrollArea(self) # استخدام QScrollArea لدعم المحتوى الطويل
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content_widget = QWidget()
        self.scroll_area.setWidget(self.scroll_content_widget)
        self.content_layout = QVBoxLayout(self.scroll_content_widget)

        self.layout.addWidget(self.scroll_area)

        self._create_widgets()
        self._update_system_info() # عرض المعلومات الأولية
        self._start_refresh_timer() # بدء تحديث المعلومات ديناميكياً

    def _create_widgets(self):
        """
        إنشاء الأدوات (Widgets) لعرض معلومات النظام.
        Creates widgets to display system information.
        """
        # معلومات عامة
        # General Information
        self.content_layout.addWidget(QLabel("<h2>System Information</h2>"))
        self.hostname_label = QLabel("Hostname: Loading...")
        self.kernel_label = QLabel("Kernel Version: Loading...")
        self.os_name_label = QLabel("OS Name: Loading...")
        self.uptime_label = QLabel("Uptime: Loading...")

        self.content_layout.addWidget(self.hostname_label)
        self.content_layout.addWidget(self.kernel_label)
        self.content_layout.addWidget(self.os_name_label)
        self.content_layout.addWidget(self.uptime_label)
        self.content_layout.addSpacing(20) # مسافة فاصلة

        # معلومات المعالج
        # CPU Information
        self.content_layout.addWidget(QLabel("<h2>CPU Information</h2>"))
        self.cpu_physical_cores_label = QLabel("Physical Cores: Loading...")
        self.cpu_logical_cores_label = QLabel("Logical Cores: Loading...")
        self.cpu_usage_label = QLabel("CPU Usage: Loading...")
        self.cpu_progress_bar = QProgressBar(self)
        self.cpu_progress_bar.setRange(0, 100) # النطاق من 0 إلى 100%

        self.content_layout.addWidget(self.cpu_physical_cores_label)
        self.content_layout.addWidget(self.cpu_logical_cores_label)
        self.content_layout.addWidget(self.cpu_usage_label)
        self.content_layout.addWidget(self.cpu_progress_bar)
        self.content_layout.addSpacing(20)

        # معلومات الذاكرة العشوائية (RAM)
        # RAM Information
        self.content_layout.addWidget(QLabel("<h2>RAM Information</h2>"))
        self.ram_total_label = QLabel("Total RAM: Loading...")
        self.ram_available_label = QLabel("Available RAM: Loading...")
        self.ram_usage_label = QLabel("RAM Usage: Loading...")
        self.ram_progress_bar = QProgressBar(self)
        self.ram_progress_bar.setRange(0, 100)

        self.content_layout.addWidget(self.ram_total_label)
        self.content_layout.addWidget(self.ram_available_label)
        self.content_layout.addWidget(self.ram_usage_label)
        self.content_layout.addWidget(self.ram_progress_bar)
        self.content_layout.addSpacing(20)

        # معلومات استخدام الأقراص
        # Disk Usage Information
        self.content_layout.addWidget(QLabel("<h2>Disk Usage (Root Partition)</h2>"))
        self.disk_total_label = QLabel("Total Disk: Loading...")
        self.disk_used_label = QLabel("Used Disk: Loading...")
        self.disk_free_label = QLabel("Free Disk: Loading...")
        self.disk_usage_label = QLabel("Disk Usage: Loading...")
        self.disk_progress_bar = QProgressBar(self)
        self.disk_progress_bar.setRange(0, 100)

        self.content_layout.addWidget(self.disk_total_label)
        self.content_layout.addWidget(self.disk_used_label)
        self.content_layout.addWidget(self.disk_free_label)
        self.content_layout.addWidget(self.disk_usage_label)
        self.content_layout.addWidget(self.disk_progress_bar)
        self.content_layout.addStretch(1) # لدفع المحتوى للأعلى

    def _update_system_info(self):
        """
        تحديث معلومات النظام وعرضها في الواجهة.
        Updates system information and displays it in the UI.
        """
        # معلومات عامة
        # General Information
        self.hostname_label.setText(f"Hostname: <b>{SystemUtils.get_hostname()}</b>")
        self.kernel_label.setText(f"Kernel Version: <b>{SystemUtils.get_kernel_version()}</b>")
        self.os_name_label.setText(f"OS Name: <b>{SystemUtils.get_os_name()}</b>")
        self.uptime_label.setText(f"Uptime: <b>{SystemUtils.get_uptime()}</b>")

        # معلومات المعالج
        # CPU Information
        cpu_info = SystemUtils.get_cpu_info()
        self.cpu_physical_cores_label.setText(f"Physical Cores: <b>{cpu_info['physical_cores']}</b>")
        self.cpu_logical_cores_label.setText(f"Logical Cores: <b>{cpu_info['logical_cores']}</b>")
        self.cpu_usage_label.setText(f"CPU Usage: <b>{cpu_info['current_usage']}%</b>")
        self.cpu_progress_bar.setValue(int(cpu_info['current_usage']))

        # معلومات الذاكرة العشوائية (RAM)
        # RAM Information
        ram_info = SystemUtils.get_ram_info()
        self.ram_total_label.setText(f"Total RAM: <b>{ram_info['total_gb']} GB</b>")
        self.ram_available_label.setText(f"Available RAM: <b>{ram_info['available_gb']} GB</b>")
        self.ram_usage_label.setText(f"RAM Usage: <b>{ram_info['used_percent']}%</b>")
        self.ram_progress_bar.setValue(int(ram_info['used_percent']))

        # معلومات استخدام الأقراص
        # Disk Usage Information
        disk_info = SystemUtils.get_disk_usage()
        self.disk_total_label.setText(f"Total Disk: <b>{disk_info['total_gb']} GB</b>")
        self.disk_used_label.setText(f"Used Disk: <b>{disk_info['used_gb']} GB</b>")
        self.disk_free_label.setText(f"Free Disk: <b>{disk_info['free_gb']} GB</b>")
        self.disk_usage_label.setText(f"Disk Usage: <b>{disk_info['used_percent']}%</b>")
        self.disk_progress_bar.setValue(int(disk_info['used_percent']))

    def _start_refresh_timer(self):
        """
        بدء مؤقت لتحديث معلومات النظام كل بضع ثوانٍ.
        Starts a timer to refresh system information every few seconds.
        """
        self.timer = QTimer(self)
        self.timer.setInterval(3000) # تحديث كل 3 ثواني (3000 ملي ثانية)
        self.timer.timeout.connect(self._update_system_info)
        self.timer.start()
