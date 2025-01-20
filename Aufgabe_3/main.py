import sys
from PyQt5.QtWidgets import QApplication
from Qt_Widget import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())



# C:\Users\hanne\AppData\Local\Programs\Python\Python312\Scripts
