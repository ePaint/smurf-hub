import os.path
from PyQt6.QtCore import Qt
from win32com.client import Dispatch
from functools import partial
from pathlib import Path
from typing import Optional
from PyQt6 import uic
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget, QLineEdit, QPushButton, QLabel, QTableWidget, QTableWidgetItem, QFileDialog
from pydantic import ValidationError
from definitions import ICON_PATH, MAIN_UI_PATH, APP_TITLE, DESKTOP_PATH, EXEC_PATH, PAYPAL_IMAGE_PATH, PAYPAL_DONATE_URL, UTILS_FOLDER
from sources.keepass import KeePassException, KeePassField, KEEPASS
from sources.popup import popup_error, popup_info
from sources.settings import SETTINGS
from sources.accounts import Account
from sources.lol_manager import login_lol_client, start_lol_client, stop_lol_client, restart_lol_client, InvalidSettings


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Init widgets
        self.settings_lol_path_input: Optional[QLineEdit] = None
        self.settings_lol_path_file_selector_button: Optional[QPushButton] = None
        self.settings_keepass_create_button: Optional[QPushButton] = None
        self.settings_keepass_path_label: Optional[QLabel] = None
        self.settings_keepass_path_input: Optional[QLineEdit] = None
        self.settings_keepass_path_file_selector_button: Optional[QPushButton] = None
        self.new_account_title_label: Optional[QLabel] = None
        self.new_account_title_input: Optional[QLineEdit] = None
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
        # Load UI
        uic.loadUi(MAIN_UI_PATH, self)
        self.setWindowTitle(APP_TITLE)
        self.setWindowIcon(QIcon(ICON_PATH))

        # Init widgets
        self.settings_lol_path_input.setText(SETTINGS.lol_path)
        self.settings_lol_path_file_selector_button.clicked.connect(self.select_lol_folder)

        self.settings_keepass_create_button.clicked.connect(self.create_keepass_file)
        self.settings_keepass_path_input.setText(SETTINGS.keepass_path)
        self.settings_keepass_path_file_selector_button.clicked.connect(self.select_keepass_file)

        self.settings_lol_path_input.returnPressed.connect(self.update_lol_path)
        self.settings_keepass_path_input.returnPressed.connect(self.update_keepass_path)

        self.new_account_add_button.clicked.connect(self.add_account)

        self.init_accounts_table()
        self.accounts_table.cellChanged.connect(self.save_accounts_table_changes)

        self.start_lol_client_button.clicked.connect(self.start_lol_client)
        self.stop_lol_client_button.clicked.connect(self.stop_lol_client)
        self.restart_lol_client_button.clicked.connect(self.restart_lol_client)

        self.paypal_button.setIcon(QIcon(PAYPAL_IMAGE_PATH))
        self.paypal_button.setIconSize(self.paypal_button.size() * 0.8)
        self.paypal_button.clicked.connect(partial(os.startfile, PAYPAL_DONATE_URL))

        self.show()

    def init_accounts_table(self):
        self.accounts_table.setColumnCount(7)
        self.accounts_table.setHorizontalHeaderLabels(['ID', 'Title', 'Username', 'Password', 'Run', 'Link', 'Delete'])
        self.accounts_table.setColumnWidth(0, 0)
        self.accounts_table.setColumnWidth(1, 80)
        self.accounts_table.setColumnWidth(2, 85)
        self.accounts_table.setColumnWidth(3, 85)
        self.accounts_table.setColumnWidth(4, 50)
        self.accounts_table.setColumnWidth(5, 50)
        self.accounts_table.setColumnWidth(6, 52)
        self.accounts_table.hideColumn(0)
        self.update_accounts_table()

    def select_lol_folder(self):
        selected_path = QFileDialog.getExistingDirectory(self, 'Select League of Legends folder', SETTINGS.lol_path)
        self.settings_lol_path_input.setText(str(Path(selected_path)))
        self.update_lol_path()

    def create_keepass_file(self):
        try:
            self.update_keepass_path(keepass_path=KEEPASS.create())
        except KeePassException as e:
            popup_error(message=str(e))
            return

    def select_keepass_file(self):
        selected_path = QFileDialog.getOpenFileName(self, 'Select KeePass file', SETTINGS.keepass_path, 'KeePass files (*.kdbx)')[0]
        self.update_keepass_path(keepass_path=selected_path, load=False)

    def add_account(self):
        try:
            account = Account(
                title=self.new_account_title_input.text(),
                username=self.new_account_username_input.text(),
                password=self.new_account_password_input.text()
            )
        except ValidationError as e:
            error_message = e.errors()[0]['msg']
            popup_error(message=error_message)
            return

        try:
            KEEPASS.add_account(account)
        except KeePassException as e:
            popup_error(message=str(e))
            return
        self.new_account_title_input.setText('')
        self.new_account_username_input.setText('')
        self.new_account_password_input.setText('')
        self.new_account_title_input.setFocus()
        self.update_accounts_table()

    def update_accounts_table(self):
        try:
            self.accounts_table.cellChanged.disconnect()
        except TypeError:
            pass

        accounts = KEEPASS.list_accounts()
        self.accounts_table.setRowCount(len(accounts))
        for i, account in enumerate(accounts):
            password_widget, execute_button, link_button, delete_button = self._get_table_buttons(account)

            self.accounts_table.setItem(i, 0, QTableWidgetItem(account.account_id))
            self.accounts_table.setItem(i, 1, QTableWidgetItem(account.title))
            self.accounts_table.setItem(i, 2, QTableWidgetItem(account.username))
            self.accounts_table.setItem(i, 3, password_widget)
            self.accounts_table.setCellWidget(i, 4, execute_button)
            self.accounts_table.setCellWidget(i, 5, link_button)
            self.accounts_table.setCellWidget(i, 6, delete_button)

        self.accounts_table.cellChanged.connect(self.save_accounts_table_changes)

    def save_accounts_table_changes(self, row, col):
        self.accounts_table.cellChanged.disconnect()
        new_value = self.accounts_table.item(row, col).text() or None

        field = None
        if col == 1:
            field = KeePassField.TITLE
        if col == 2:
            field = KeePassField.USERNAME
        if col == 3:
            field = KeePassField.PASSWORD
            self.accounts_table.item(row, col).setText('******')
        if field is None:
            return

        account_id = self.accounts_table.item(row, 0).text() or None

        if not new_value:
            account = KEEPASS.get_account(account_id=account_id)
            old_value = account.__getattribute__(field.value)
            self.accounts_table.item(row, col).setText(old_value)
            popup_error(message=f'Invalid {field.value} value')
            return

        KEEPASS.update_account_field(account_id=account_id, field=field, value=new_value)

        if field.PASSWORD:
            self.accounts_table.item(row, col).setData(Qt.ItemDataRole.BackgroundRole, new_value)

        self.accounts_table.cellChanged.connect(self.save_accounts_table_changes)

    def update_lol_path(self):
        lol_path = self.settings_lol_path_input.text()
        if lol_path and not os.path.exists(lol_path):
            popup_error(message='Invalid League of Legends path')
            self.settings_lol_path_input.setText(SETTINGS.lol_path)
            return

        SETTINGS.set_lol_path(lol_path)
        SETTINGS.save()

    def update_keepass_path(self, keepass_path: str = None, load: bool = True):
        if keepass_path is None:
            keepass_path = self.settings_keepass_path_input.text()
            if not keepass_path:
                return

        if keepass_path == SETTINGS.keepass_path:
            return

        self.settings_keepass_path_input.setText(keepass_path)
        if keepass_path and not os.path.exists(keepass_path):
            popup_error(message='Invalid KeePass path')
            self.settings_keepass_path_input.setText(SETTINGS.keepass_path)
            return

        previous_keepass_path = SETTINGS.keepass_path
        SETTINGS.keepass_path = keepass_path
        try:
            if load:
                KEEPASS.reload()
        except KeePassException as e:
            popup_error(message=str(e))
            SETTINGS.keepass_path = previous_keepass_path
            self.settings_keepass_path_input.setText(previous_keepass_path)

        SETTINGS.save()
        self.update_accounts_table()

    def process_delete(self, account_id: str):
        self.unsetCursor()
        KEEPASS.delete_account(account_id=account_id)
        self.update_accounts_table()

    @staticmethod
    def create_shortcut(account_id: str, title: str):
        if not os.path.exists(UTILS_FOLDER):
            os.makedirs(str(UTILS_FOLDER))

        vbs_file_path = str(UTILS_FOLDER.joinpath(f'{title}-login.vbs'))
        lnk_file_path = str(DESKTOP_PATH.joinpath(f'Start LoL as {title}.lnk'))
        with open(vbs_file_path, 'w+') as f:
            f.writelines([
                'Set objShell = CreateObject("WScript.Shell")\n',
                f'customCommand = """{EXEC_PATH}"" --account-id ""{account_id}"""\n',
                'objShell.Run customCommand, 0, True'
            ])
        shell = Dispatch('WScript.Shell')
        shortcut_file = shell.CreateShortCut(lnk_file_path)
        shortcut_file.Targetpath = vbs_file_path
        shortcut_file.IconLocation = ICON_PATH
        shortcut_file.WindowStyle = 7
        shortcut_file.save()
        popup_info(message=f'Shortcut created for {title} in Desktop')

    @staticmethod
    def start_lol_client():
        try:
            start_lol_client()
        except InvalidSettings as e:
            print(e)
            popup_error(message=str(e))

    @staticmethod
    def stop_lol_client():
        try:
            stop_lol_client()
        except InvalidSettings as e:
            print(e)
            popup_error(message=str(e))

    @staticmethod
    def restart_lol_client():
        try:
            restart_lol_client()
        except InvalidSettings as e:
            print(e)
            popup_error(message=str(e))

    def _get_table_buttons(self, account: Account):
        account_id = account.account_id
        title = account.title
        password = account.password

        password_widget: QTableWidgetItem = QTableWidgetItem()
        password_widget.setData(Qt.ItemDataRole.BackgroundRole, password)
        password_widget.setText("******")

        execute_button = QPushButton('🚀')
        execute_button.setObjectName(f'execute_button_{account_id}')
        execute_button.setToolTip(f'Run League of Legends as {title}')
        execute_button.clicked.connect(partial(login_lol_client, account_id))

        link_button = QPushButton('📑')
        link_button.setObjectName(f'link_button_{account_id}')
        link_button.setToolTip(f'Create shortcut for {title}')
        link_button.clicked.connect(partial(self.create_shortcut, account_id, title))

        delete_button = QPushButton('❌️')
        delete_button.setObjectName(f'delete_button_{account_id}')
        delete_button.setToolTip(f'Delete {title}')
        delete_button.clicked.connect(partial(self.process_delete, account_id))

        return password_widget, execute_button, link_button, delete_button
