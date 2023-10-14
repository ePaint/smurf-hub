from PyQt6 import uic
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QDialog
from definitions import ICON_PATH, PASSWORD_UI_PATH, APP_TITLE, APP_MANAGER
from sources.app import AppSource


def get_password(title: str = APP_TITLE, message: str = 'Enter KeePass Password:'):
    popup = QDialog()
    uic.loadUi(PASSWORD_UI_PATH, popup)
    popup.setWindowTitle(title)
    popup.password_label.setText(message)
    popup.setWindowIcon(QIcon(ICON_PATH))

    popup.password_input.returnPressed.connect(popup.close)

    popup.show()
    popup.exec()

    password = popup.password_input.text()

    return password
