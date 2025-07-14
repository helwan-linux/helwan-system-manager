import sys
import os

# هذا الكود يضمن أن المسار الذي يحتوي على مجلد 'src' يتم إضافته إلى sys.path
# بحيث يمكن استيراد الوحدات الداخلية مثل 'src.ui' أو 'src.core'.
# This code ensures that the directory containing the 'src' folder is added to sys.path
# so that internal modules like 'src.ui' or 'src.core' can be imported.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# الآن يمكن استيراد الوحدات من src/ بثقة
from src.ui.main_window import MainWindow
from PyQt5.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())
