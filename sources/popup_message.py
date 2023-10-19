from PyQt6 import uic
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QDialog
from definitions import ICON_PATH, ICON_ERROR_PATH, MESSAGE_UI_PATH, APP_TITLE, APP_MANAGER
from sources.app import AppSource


def error_popup(message: str = 'Error', title: str = APP_TITLE + ' - Error'):
    message_popup(message=message, title=title, icon=ICON_ERROR_PATH)


def message_popup(message: str = '', title: str = APP_TITLE, icon: str = ICON_PATH):
    popup = QDialog()
    uic.loadUi(MESSAGE_UI_PATH, popup)
    popup.setWindowTitle(title)
    popup.message_label.setText(message)
    popup.setWindowIcon(QIcon(icon))

    popup.ok_button.clicked.connect(popup.close)

    if APP_MANAGER.source != AppSource.MAIN_WINDOW:
        popup.ok_button.clicked.connect(APP_MANAGER.stop)

    popup.show()

    if APP_MANAGER.source == AppSource.MAIN_WINDOW:
        popup.exec()
    elif not APP_MANAGER.is_running:
        APP_MANAGER.start(AppSource.PASSWORD_POPUP)
