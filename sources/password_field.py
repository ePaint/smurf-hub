from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QLineEdit, QPushButton, QVBoxLayout

from sources.accounts import Account


class PasswordWidget(QWidget):
    def __init__(self, account: Account):
        super().__init__()

        self.setFixedWidth(80)
        self.setFixedHeight(23)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.line_edit = QLineEdit()
        self.line_edit.setText(account.password)
        self.line_edit.setFixedWidth(60)
        self.line_edit.setFixedHeight(23)

        self.show_hide_button = QPushButton("👁️")
        self.show_hide_button.setFixedWidth(20)
        self.show_hide_button.setFixedHeight(23)

        self.show_hide_button.setCheckable(True)
        self.show_hide_button.toggled.connect(self.toggle_password_visibility)

        self.layout.addWidget(self.line_edit, 1, Qt.AlignmentFlag.AlignLeft)
        # self.layout.addWidget(self.show_hide_button)

        self.layout.addWidget(self.show_hide_button, 1, Qt.AlignmentFlag.AlignTop)

        self.setLayout(self.layout)

    def toggle_password_visibility(self, checked):
        if checked:
            self.line_edit.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.line_edit.setEchoMode(QLineEdit.EchoMode.Password)

    def setText(self, text: str):
        self.line_edit.setText(text)




