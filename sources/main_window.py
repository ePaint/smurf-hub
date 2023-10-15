import os.path
from win32com.client import Dispatch
from functools import partial
from pathlib import Path
from typing import Optional
from PyQt6 import uic
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget, QLineEdit, QPushButton, QLabel, QTableWidget, QTableWidgetItem, QFileDialog
from pydantic import ValidationError
from definitions import PROJECT_FOLDER, PYTHON_VENV_PATH, ICON_PATH, LOL_MANAGER_PATH, MAIN_UI_PATH, APP_TITLE, DESKTOP_PATH, EXEC_PATH, VBS_FOLDER, PAYPAL_IMAGE_PATH, PAYPAL_DONATE_URL
from sources.popup_message import error_popup, message_popup
from sources.settings import SETTINGS
from sources.accounts import ACCOUNTS, Account, Accounts
from sources.lol_manager import login_lol_client, LoginBehavior, start_lol_client, stop_lol_client, restart_lol_client, InvalidSettings


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.settings_lol_path_input: Optional[QLineEdit] = None
        self.settings_lol_path_file_selector_button: Optional[QPushButton] = None
        self.settings_use_keepass_button: Optional[QPushButton] = None
        self.settings_keepass_path_label: Optional[QLabel] = None
        self.settings_keepass_path_input: Optional[QLineEdit] = None
        self.settings_keepass_path_file_selector_button: Optional[QPushButton] = None
        self.new_account_name_label: Optional[QLabel] = None
        self.new_account_name_input: Optional[QLineEdit] = None
        self.new_account_keepass_reference_label: Optional[QLabel] = None
        self.new_account_keepass_reference_input: Optional[QLineEdit] = None
        self.new_account_username_label: Optional[QLabel] = None
        self.new_account_username_input: Optional[QLineEdit] = None
        self.new_account_password_label: Optional[QLabel] = None
        self.new_account_password_input: Optional[QLineEdit] = None
        self.new_account_add_button: Optional[QPushButton] = None
        self.accounts_table: Optional[QTableWidget] = None
        self.start_lol_client_button: Optional[QPushButton] = None
        self.stop_lol_client_button: Optional[QPushButton] = None
        self.restart_lol_client_button: Optional[QPushButton] = None
        self.paypal_button: Optional[QPushButton] = None

    def start_app(self):
        uic.loadUi(MAIN_UI_PATH, self)
        self.setWindowTitle(APP_TITLE)
        self.setWindowIcon(QIcon(ICON_PATH))

        # Init widgets
        self.settings_lol_path_input.setText(SETTINGS.lol_path)
        self.settings_lol_path_file_selector_button.clicked.connect(self.select_lol_folder)

        self.settings_use_keepass_button.setChecked(SETTINGS.keepass_enabled)
        self.settings_keepass_path_input.setText(SETTINGS.keepass_path)
        self.settings_keepass_path_file_selector_button.clicked.connect(self.select_keepass_file)

        self.settings_lol_path_input.returnPressed.connect(self.save_settings)
        self.settings_use_keepass_button.clicked.connect(self.toggle_keepass)
        self.settings_use_keepass_button.clicked.connect(self.save_settings)
        self.settings_keepass_path_input.returnPressed.connect(self.save_settings)

        self.new_account_add_button.clicked.connect(self.add_account)
        self.toggle_keepass()

        self.init_accounts_table()
        self.accounts_table.cellChanged.connect(self.save_accounts_table_changes)

        self.start_lol_client_button.clicked.connect(self.start_lol_client)
        self.stop_lol_client_button.clicked.connect(self.stop_lol_client)
        self.restart_lol_client_button.clicked.connect(self.restart_lol_client)

        self.paypal_button.setIcon(QIcon(PAYPAL_IMAGE_PATH))
        self.paypal_button.setIconSize(self.paypal_button.size() * 0.8)
        self.paypal_button.clicked.connect(partial(os.startfile, PAYPAL_DONATE_URL))

        self.show()

    def select_lol_folder(self):
        selected_path = QFileDialog.getExistingDirectory(self, 'Select League of Legends folder', SETTINGS.lol_path)
        SETTINGS.set_lol_path(str(Path(selected_path)))
        self.settings_lol_path_input.setText(SETTINGS.lol_path)
        SETTINGS.save()

    def select_keepass_file(self):
        selected_path = QFileDialog.getOpenFileName(self, 'Select KeePass file', SETTINGS.keepass_path, 'KeePass files (*.kdbx)')[0]
        SETTINGS.keepass_path = str(Path(selected_path))
        self.settings_keepass_path_input.setText(SETTINGS.keepass_path)
        SETTINGS.save()

    def add_account(self):
        try:
            account = Account(
                name=self.new_account_name_input.text() or None,
                keepass_enabled=SETTINGS.keepass_enabled,
                keepass_reference=self.new_account_keepass_reference_input.text() or None,
                username=self.new_account_username_input.text() or None,
                password=self.new_account_password_input.text() or None
            )
        except ValidationError as e:
            message = e.errors()[0]['msg']
            print(message)
            error_popup(message=message)
            return
        self.new_account_name_input.setText('')
        self.new_account_keepass_reference_input.setText('')
        self.new_account_username_input.setText('')
        self.new_account_password_input.setText('')
        ACCOUNTS.add(account)
        ACCOUNTS.save()
        self.update_accounts_table()
        self.new_account_add_button.setFocus()

    def init_accounts_table(self):
        self.accounts_table.setColumnCount(7)
        self.accounts_table.setHorizontalHeaderLabels(['Name', 'KeePass Reference', 'Username', 'Password', 'Run', 'Link', 'Delete'])
        self.accounts_table.setColumnWidth(0, 84)
        self.accounts_table.setColumnWidth(1, 170)
        self.accounts_table.setColumnWidth(2, 85)
        self.accounts_table.setColumnWidth(3, 85)
        self.accounts_table.setColumnWidth(4, 50)
        self.accounts_table.setColumnWidth(5, 50)
        self.accounts_table.setColumnWidth(6, 50)
        self.update_accounts_table()

    def update_accounts_table(self):
        try:
            self.accounts_table.cellChanged.disconnect()
        except TypeError as e:
            pass
        self.accounts_table.setRowCount(len(ACCOUNTS.accounts))
        for i, account in enumerate(ACCOUNTS.accounts.values()):
            self.accounts_table.setItem(i, 0, QTableWidgetItem(account.name))
            self.accounts_table.setItem(i, 1, QTableWidgetItem(account.keepass_reference))
            self.accounts_table.setItem(i, 2, QTableWidgetItem(account.username))
            self.accounts_table.setItem(i, 3, QTableWidgetItem(account.password))

            execute_button = QPushButton('🚀')
            execute_button.setObjectName(f'execute_button_{i}')
            execute_button.setToolTip(f'Run League of Legends as {account.name} using {"KeePass" if SETTINGS.keepass_enabled else "username and password"}')
            execute_button.clicked.connect(partial(login_lol_client, account.name, LoginBehavior.USE_SETTINGS))

            link_button = QPushButton('📑')
            link_button.setObjectName(f'link_button_{i}')
            link_button.setToolTip(f'Create shortcut for {account.name} using {"KeePass" if SETTINGS.keepass_enabled else "username and password"}')
            link_button.clicked.connect(partial(self.create_shortcut, account.name))

            delete_button = QPushButton('❌️')
            delete_button.setObjectName(f'delete_button_{i}')
            delete_button.setToolTip(f'Delete {account.name}')
            delete_button.clicked.connect(partial(self.process_delete, i))

            self.accounts_table.setCellWidget(i, 4, execute_button)
            self.accounts_table.setCellWidget(i, 5, link_button)
            self.accounts_table.setCellWidget(i, 6, delete_button)
        self.accounts_table.setColumnHidden(1, not SETTINGS.keepass_enabled)
        self.accounts_table.setColumnHidden(2, SETTINGS.keepass_enabled)
        self.accounts_table.setColumnHidden(3, SETTINGS.keepass_enabled)
        self.accounts_table.cellChanged.connect(self.save_accounts_table_changes)

    def save_accounts_table_changes(self):
        print('RUNNING SAVE ACCOUNTS TABLE CHANGES')
        NEW_ACCOUNTS = Accounts()
        for i in range(self.accounts_table.rowCount()):
            is_deleted = self.accounts_table.cellWidget(i, 5).isChecked()
            if is_deleted:
                print('DELETED', i)
                continue
            print('ROW COUNT', self.accounts_table.rowCount(), 'INDEX', i)
            name = self.accounts_table.item(i, 0).text() or None
            keepass_reference = self.accounts_table.item(i, 1).text() or None
            username = self.accounts_table.item(i, 2).text() or None
            password = self.accounts_table.item(i, 3).text() or None
            print('username', username)
            print('password', password)
            account = Account(
                name=name,
                keepass_reference=keepass_reference,
                username=username,
                password=password
            )
            print('account', account)
            NEW_ACCOUNTS.add(account)
        ACCOUNTS.accounts = NEW_ACCOUNTS.accounts
        ACCOUNTS.save()

    def toggle_keepass(self):
        SETTINGS.keepass_enabled = self.settings_use_keepass_button.isChecked()
        self.setWindowTitle(APP_TITLE + ' (KeePass)' if SETTINGS.keepass_enabled else APP_TITLE)

        style = 'color: #999999;' if not SETTINGS.keepass_enabled else ''
        inverted_style = 'color: #999999;' if SETTINGS.keepass_enabled else ''
        self.settings_keepass_path_label.setStyleSheet(style)
        self.new_account_keepass_reference_label.setStyleSheet(style)
        self.new_account_username_label.setStyleSheet(inverted_style)
        self.new_account_password_label.setStyleSheet(inverted_style)

        self.settings_keepass_path_input.setStyleSheet(style)
        self.settings_keepass_path_file_selector_button.setStyleSheet(style)
        self.new_account_keepass_reference_input.setStyleSheet(style)
        self.new_account_username_input.setStyleSheet(inverted_style)
        self.new_account_password_input.setStyleSheet(inverted_style)

        self.settings_keepass_path_input.setDisabled(not SETTINGS.keepass_enabled)
        self.settings_keepass_path_file_selector_button.setDisabled(not SETTINGS.keepass_enabled)
        self.new_account_keepass_reference_input.setDisabled(not SETTINGS.keepass_enabled)
        self.new_account_username_input.setDisabled(SETTINGS.keepass_enabled)
        self.new_account_password_input.setDisabled(SETTINGS.keepass_enabled)
        self.update_accounts_table()

    def save_settings(self):
        lol_path = self.settings_lol_path_input.text()
        if lol_path and not os.path.exists(lol_path):
            error_popup(message='Invalid League of Legends path')
            self.settings_lol_path_input.setText(SETTINGS.lol_path)
            return

        keepass_path = self.settings_keepass_path_input.text()
        if keepass_path and not os.path.exists(keepass_path):
            error_popup(message='Invalid KeePass path')
            self.settings_keepass_path_input.setText(SETTINGS.keepass_path)
            return

        SETTINGS.set_lol_path(lol_path)
        SETTINGS.keepass_path = keepass_path
        SETTINGS.save()

    def process_delete(self, index: int):
        self.unsetCursor()
        ACCOUNTS.delete(index)
        ACCOUNTS.save()
        self.update_accounts_table()

    @staticmethod
    def create_shortcut(name: str):
        account = ACCOUNTS.get_account(name)
        if not account:
            return

        if not os.path.exists(VBS_FOLDER):
            os.makedirs(str(VBS_FOLDER))

        vbs_file_path = str(VBS_FOLDER.joinpath(f'{name}-login{"-keepass" if SETTINGS.keepass_enabled else ""}.vbs'))
        lnk_file_path = str(DESKTOP_PATH.joinpath(f'Start LoL as {name}{" (KeePass)" if SETTINGS.keepass_enabled else ""}.lnk'))
        behavior = 'use_keepass' if SETTINGS.keepass_enabled else 'use_credentials'
        with open(vbs_file_path, 'w+') as f:
            f.writelines([
                'Set objShell = CreateObject("WScript.Shell")\n',
                f'customCommand = """{EXEC_PATH}"" --name ""{name}"" --behavior ""{behavior}"""\n',
                'objShell.Run customCommand, 0, True'
            ])
        shell = Dispatch('WScript.Shell')
        shortcut_file = shell.CreateShortCut(lnk_file_path)
        shortcut_file.Targetpath = vbs_file_path
        shortcut_file.IconLocation = ICON_PATH
        shortcut_file.WindowStyle = 7
        shortcut_file.save()
        message_popup(message=f'Shortcut created for {name}{" (KeePass)" if SETTINGS.keepass_enabled else ""} in Desktop')

    @staticmethod
    def start_lol_client():
        try:
            start_lol_client()
        except InvalidSettings as e:
            print(e)
            error_popup(message=str(e))

    @staticmethod
    def stop_lol_client():
        try:
            stop_lol_client()
        except InvalidSettings as e:
            print(e)
            error_popup(message=str(e))

    @staticmethod
    def restart_lol_client():
        try:
            restart_lol_client()
        except InvalidSettings as e:
            print(e)
            error_popup(message=str(e))
