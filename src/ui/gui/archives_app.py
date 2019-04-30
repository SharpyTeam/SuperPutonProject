import sys

from PyQt5 import QtWidgets
import src.ui.gui.archives_design as archives_design


class ArchivesApp(QtWidgets.QMainWindow, archives_design.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

    def exit_app(self):
        self.close()

    @staticmethod
    def run():
        app = QtWidgets.QApplication(sys.argv)
        window = ArchivesApp()
        window.show()
        sys.exit(app.exec())
