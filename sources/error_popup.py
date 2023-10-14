from PyQt6 import uic
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QDialog
from definitions import ICON_PATH, ERROR_UI_PATH, APP_TITLE, APP_MANAGER
from sources.app import AppSource


def error_popup(title: str = APP_TITLE, message: str = 'Error'):
    popup = QDialog()
    uic.loadUi(ERROR_UI_PATH, popup)
    popup.setWindowTitle(title + ' - Error')
    popup.error_label.setText(message)
    popup.setWindowIcon(QIcon(ICON_PATH))

    popup.ok_button.clicked.connect(popup.close)

    if APP_MANAGER.source != AppSource.MAIN_WINDOW:
        popup.ok_button.clicked.connect(APP_MANAGER.stop)

    popup.show()

    if APP_MANAGER.source == AppSource.MAIN_WINDOW:
        popup.exec()
    elif not APP_MANAGER.is_running:
        APP_MANAGER.start(AppSource.PASSWORD_POPUP)
