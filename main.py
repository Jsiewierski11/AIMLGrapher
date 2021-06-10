import sys
from PyQt5.QtWidgets import QApplication

from GUI.EditorWindow import EditorWindow
import Utils.Storage as Storage
import xml.etree.ElementTree as ET


if __name__ == '__main__':
    app = QApplication(sys.argv)

    wnd = EditorWindow()
    try:
        sys.exit(app.exec_())
    except:
        pass

