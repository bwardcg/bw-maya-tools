###############################
#
#   Basic Mayu UI for inhereting into my Tools GUIs
#
#   Author:  Brian Ward  bwardcg@gmail.com  www.brianward.work
#
#   Requires:  bw_ui_maya
#
###############################

# Maya 2017-2024 used PySide2
# Maya 2025+ is PySide6
from PySide6 import QtWidgets, QtCore
from shiboken6 import wrapInstance
from maya import OpenMayaUI as omui

def get_maya_main_window():
    """Return the Maya main window as a QWidget."""
    ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(ptr), QtWidgets.QWidget)

class MayaWindowBase(QtWidgets.QWidget):
    """
    A base QWidget for PySide6 tools in Maya 2025+.
    Provides automatic parenting, layout, and singleton-style launch.
    Other UIs can inherit this class and (hopefully) not worry about QT versions
    """
    _instances = {}  # one instance per subclass

    def __init__(self, title='Window', width=400, height=300):
        super().__init__(parent=get_maya_main_window())

        self.setWindowTitle(title)
        self.setMinimumSize(width, height)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Window)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.layout)

    def showEvent(self, event):
        # raise and active window on create
        self.raise_()
        self.activateWindow()
        super().showEvent(event)

    @classmethod
    def launch(cls, *args, **kwargs):
        """
        Creates and shows a new UI instance after closing any existing ones of the same class.
        """
        # Close any open windows of this class
        for w in QtWidgets.QApplication.topLevelWidgets():
            if isinstance(w, cls):
                try:
                    w.close()
                    w.deleteLater()
                except:
                    pass

        instance = cls(*args, **kwargs)
        instance.show()

        # redundant to showEvent, in case show() is run elsewhere
        instance.raise_()
        instance.activateWindow()
        return instance
