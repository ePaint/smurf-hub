from typing import Optional
from PyQt6 import uic
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QDialog, QLabel, QLineEdit
from definitions import PASSWORD_UI_PATH, APP_TITLE, ICON_PATH, APP_MANAGER
from sources.app import AppSource


class PasswordPopup(QDialog):
    def __init__(self, error_message: str = ''):
        super().__init__()
        self.error_message: str = error_message
        self.password_label: Optional[QLabel] = None
        self.password_input: Optional[QLineEdit] = None
        self.error_label: Optional[QLabel] = None
        self.password: Optional[str] = None
        self.submitted: Optional[bool] = False

    def get_password(self):
        uic.loadUi(PASSWORD_UI_PATH, self)
        self.setWindowTitle(APP_TITLE)
        self.setWindowIcon(QIcon(ICON_PATH))
        self.password_label.setText('Enter KeePass Password:')
        self.password_input.returnPressed.connect(self._handle_close)
        self.error_label.setText(self.error_message)
        self.show()

        if APP_MANAGER.is_running:
            self.exec()
        else:
            APP_MANAGER.start(AppSource.PASSWORD_POPUP)

        self.raise_()

    def _handle_close(self):
        self.password = self.password_input.text()

        if not self.password:
            self.error_label.setText('Password cannot be empty')
            return

        self.submitted = True
        self.close()

        if APP_MANAGER.source == AppSource.PASSWORD_POPUP:
            APP_MANAGER.stop()
