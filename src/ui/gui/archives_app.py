import sys

from PyQt5 import QtWidgets
import src.ui.gui.archives_design as archives_design


class ArchivesApp(QtWidgets.QMainWindow, archives_design.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.menu.triggered.connect(self.exit_app)
        self.pushButton.clicked.connect(self.change_label)

    def change_label(self):
        self.label.setText("Чего жмёшь, а?")

    def exit_app(self):
        self.close()

    @staticmethod
    def run():
        app = QtWidgets.QApplication(sys.argv)
        window = ArchivesApp()
        window.show()
        sys.exit(app.exec())
