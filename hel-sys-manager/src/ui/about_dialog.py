from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt
import os

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        """
        تهيئة نافذة "حول" التطبيق.
        Initializes the "About" dialog.
        """
        super().__init__(parent)
        self.setWindowTitle("About hel-sys-manager")
        self.setFixedSize(400, 300) # تعيين حجم ثابت للنافذة

        self._setup_ui()

    def _setup_ui(self):
        """
        إعداد واجهة المستخدم لنافذة "حول".
        Sets up the user interface for the "About" dialog.
        """
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter) # محاذاة المحتوى في المنتصف

        # إضافة اللوجو
        # Add the logo
        logo_label = QLabel()
        try:
            # المسار نسبيًا لمكان تشغيل main.py
            # Path is relative to where main.py is run
            logo_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'images', 'logo.png')
            logo_pixmap = QPixmap(logo_path)
            if not logo_pixmap.isNull():
                logo_label.setPixmap(logo_pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                logo_label.setAlignment(Qt.AlignCenter)
            else:
                logo_label.setText("Logo Missing") # رسالة في حال عدم وجود الصورة
                logo_label.setAlignment(Qt.AlignCenter)
        except Exception as e:
            logo_label.setText(f"Error loading logo: {e}") # رسالة في حال حدوث خطأ أثناء التحميل
            logo_label.setAlignment(Qt.AlignCenter)


        # اسم التطبيق
        # Application Name
        app_name_label = QLabel("<h1>hel-sys-manager</h1>")
        app_name_label.setAlignment(Qt.AlignCenter)
        
        # الوصف
        # Description
        description_label = QLabel("A powerful Arch Linux system management \nand customization assistant.")
        description_label.setAlignment(Qt.AlignCenter)
        description_label.setFont(QFont("SansSerif", 10))

        # الإصدار
        # Version
        version_label = QLabel("Version: 0.1.0")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setFont(QFont("SansSerif", 9))

        # حقوق الطبع والنشر
        # Copyright
        copyright_label = QLabel("© 2025 hel-sys-manager Team.")
        copyright_label.setAlignment(Qt.AlignCenter)
        copyright_label.setFont(QFont("SansSerif", 8))

        # زر الإغلاق
        # Close Button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        close_button.setFixedSize(100, 30) # تعيين حجم ثابت للزر


        layout.addWidget(logo_label)
        layout.addWidget(app_name_label)
        layout.addWidget(description_label)
        layout.addWidget(version_label)
        layout.addWidget(copyright_label)
        layout.addStretch() # لدفع الزر للأسفل
        layout.addWidget(close_button, alignment=Qt.AlignCenter)
