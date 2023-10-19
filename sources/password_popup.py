from functools import partial
from PyQt6 import uic
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QDialog
from definitions import ICON_PATH, PASSWORD_UI_PATH, APP_TITLE, APP_MANAGER
from sources.app import AppSource


class InvalidPassword(Exception):
    def __init__(self, message):
        super().__init__(message)


def get_password(title: str = APP_TITLE, message: str = 'Enter KeePass Password:', error_message: str = ''):
    popup = QDialog()
    uic.loadUi(PASSWORD_UI_PATH, popup)
    popup.setWindowTitle(title)
    popup.password_label.setText(message)
    popup.error_label.setText(error_message)
    popup.setWindowIcon(QIcon(ICON_PATH))
    popup.password_input.returnPressed.connect(partial(close_popup, popup))
    popup.show()

    if APP_MANAGER.is_running:
        popup.exec()
    else:
        APP_MANAGER.start(AppSource.PASSWORD_POPUP)
        popup.password_input.returnPressed.connect(APP_MANAGER.stop)

    password = popup.password_input.text()

    if not password:
        raise InvalidPassword('Password cannot be empty')

    return password


def close_popup(popup: QDialog):
    password = popup.password_input.text()

    if not password:
        popup.error_label.setText('Password cannot be empty')
        return

    popup.close()
