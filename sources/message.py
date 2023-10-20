from typing import Optional
from PyQt6 import uic
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QDialog, QLabel, QPushButton
from definitions import MESSAGE_UI_PATH, APP_MANAGER, APP_TITLE, ICON_ERROR_PATH, ICON_PATH
from sources.app import AppSource


class MessagePopup(QDialog):
    def __init__(self):
        super().__init__()
        self.message_label: Optional[QLabel] = None
        self.ok_button: Optional[QPushButton] = None

    def info(self, message: str):
        self._display(message=message, title=APP_TITLE, icon=ICON_PATH)

    def error(self, message: str):
        self._display(message=message, title=APP_TITLE + ' - Error', icon=ICON_ERROR_PATH)

    def _display(self, message: str, title: str, icon: str):
        uic.loadUi(MESSAGE_UI_PATH, self)
        self.setWindowTitle(title)
        self.message_label.setText(message)
        self.setWindowIcon(QIcon(icon))
        self.ok_button.clicked.connect(self._handle_close)
        self.show()

        if APP_MANAGER.is_running:
            self.exec()
        else:
            APP_MANAGER.start(AppSource.PASSWORD_POPUP)

    def _handle_close(self):
        self.close()

        if APP_MANAGER.source == AppSource.PASSWORD_POPUP:
            APP_MANAGER.stop()
