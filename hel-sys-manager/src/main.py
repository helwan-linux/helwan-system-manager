import sys
import os

# بما أن main.py الآن داخل src/، فإن الدليل الجذر للمشروع هو المجلد الذي يحتوي على src/
# Therefore, the project root is the directory containing src/
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)


# الآن يتم استيراد main_window من المسار المطلق src.ui
# Now main_window is imported from the absolute path src.ui
from src.ui.main_window import MainWindow # <--- تأكد أن هذا هو سطر الاستيراد هنا

from PyQt5.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())
