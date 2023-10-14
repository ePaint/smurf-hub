import os.path
from functools import partial
from typing import Optional
from PyQt6 import uic
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget, QLineEdit, QPushButton, QLabel, QTableWidget, QTableWidgetItem, QStyle
from win32com.client import Dispatch
from definitions import PROJECT_FOLDER, PYTHON_VENV_PATH, ICON_PATH, LOL_MANAGER_PATH, MAIN_UI_PATH, APP_TITLE, APP_MANAGER
from sources.settings import SETTINGS
from sources.accounts import ACCOUNTS, Account, Accounts
from lol_manager import login_lol_client, LoginBehavior, start_lol_client, stop_lol_client, restart_lol_client


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.settings_lol_path_input: Optional[QLineEdit] = None
        self.settings_use_keepass_button: Optional[QPushButton] = None
        self.settings_keepass_path_label: Optional[QLabel] = None
        self.settings_keepass_path_input: Optional[QLineEdit] = None
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

    def start_app(self):
        uic.loadUi(MAIN_UI_PATH, self)
        self.setWindowTitle(APP_TITLE)
        self.setWindowIcon(QIcon(ICON_PATH))

        # Init widgets
        self.settings_lol_path_input.setText(SETTINGS.lol_path)
        self.settings_use_keepass_button.setChecked(SETTINGS.keepass_enabled)
        self.settings_keepass_path_input.setText(SETTINGS.keepass_path)

        self.settings_lol_path_input.editingFinished.connect(self.save_settings)
        self.settings_use_keepass_button.clicked.connect(self.toggle_keepass)
        self.settings_use_keepass_button.clicked.connect(self.save_settings)
        self.settings_keepass_path_input.editingFinished.connect(self.save_settings)

        self.new_account_add_button.clicked.connect(self.add_account)
        self.toggle_keepass()

        self.init_accounts_table()
        self.accounts_table.cellChanged.connect(self.save_accounts_table_changes)

        self.start_lol_client_button.clicked.connect(start_lol_client)
        self.stop_lol_client_button.clicked.connect(stop_lol_client)
        self.restart_lol_client_button.clicked.connect(restart_lol_client)

        self.show()

    def add_account(self):
        try:
            account = Account(
                name=self.new_account_name_input.text() or None,
                keepass_enabled=SETTINGS.keepass_enabled,
                keepass_reference=self.new_account_keepass_reference_input.text() or None,
                username=self.new_account_username_input.text() or None,
                password=self.new_account_password_input.text() or None
            )
        except ValueError as e:
            print(e)
            return
        self.new_account_name_input.setText('')
        self.new_account_keepass_reference_input.setText('')
        self.new_account_username_input.setText('')
        self.new_account_password_input.setText('')
        ACCOUNTS.add(account)
        ACCOUNTS.save()
        self.update_accounts_table()

    def init_accounts_table(self):
        self.accounts_table.setColumnCount(7)
        self.accounts_table.setHorizontalHeaderLabels(['Name', 'Keepass Ref', 'Username', 'Password', 'Run', 'Link', 'Delete'])
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
            execute_button.clicked.connect(partial(login_lol_client, account.name, LoginBehavior.USE_SETTINGS))

            link_button = QPushButton('📑')
            link_button.setObjectName(f'link_button_{i}')
            link_button.clicked.connect(partial(self.create_shortcut, account.name))

            delete_button = QPushButton('❌️')
            delete_button.setObjectName(f'delete_button_{i}')
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
        self.new_account_keepass_reference_input.setStyleSheet(style)
        self.new_account_username_input.setStyleSheet(inverted_style)
        self.new_account_password_input.setStyleSheet(inverted_style)

        self.settings_keepass_path_input.setDisabled(not SETTINGS.keepass_enabled)
        self.new_account_keepass_reference_input.setDisabled(not SETTINGS.keepass_enabled)
        self.new_account_username_input.setDisabled(SETTINGS.keepass_enabled)
        self.new_account_password_input.setDisabled(SETTINGS.keepass_enabled)
        self.update_accounts_table()

    def save_settings(self):
        lol_path = self.settings_lol_path_input.text()
        if not os.path.exists(lol_path):
            return

        keepass_path = self.settings_keepass_path_input.text()
        if keepass_path and not os.path.exists(keepass_path):
            return

        SETTINGS.lol_path = lol_path
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
        vbs_file_path = str(PROJECT_FOLDER.joinpath('vbs').joinpath(f'{name}-login{"-keepass" if SETTINGS.keepass_enabled else ""}.vbs'))
        lnk_file_path = str(PROJECT_FOLDER.joinpath('shortcuts').joinpath(f'Start LoL as {name}{" (KeePass)" if SETTINGS.keepass_enabled else ""}.lnk'))
        behavior = 'always_use_keepass' if SETTINGS.keepass_enabled else 'never_use_keepass'
        with open(vbs_file_path, 'w+') as f:
            f.writelines([
                'Set objShell = CreateObject("WScript.Shell")\n',
                f'pythonCommand = """{PYTHON_VENV_PATH}"" ""{LOL_MANAGER_PATH}"" --name ""{name}"" --behavior {behavior}"\n',
                'objShell.Run pythonCommand, 0, True'
            ])
        shell = Dispatch('WScript.Shell')
        shortcut_file = shell.CreateShortCut(lnk_file_path)
        shortcut_file.Targetpath = vbs_file_path
        shortcut_file.IconLocation = ICON_PATH
        shortcut_file.WindowStyle = 7
        shortcut_file.save()

