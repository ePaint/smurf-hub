import os
from enum import Enum
from typing import Optional
from pykeepass import PyKeePass, create_database
from pykeepass.entry import Entry
from pykeepass.exceptions import CredentialsError
from pykeepass.group import Group
from definitions import EXEC_FOLDER, APP_TITLE, KEEPASS_CREATE_PATH
from sources.accounts import Account
from sources.password_popup import get_password, InvalidPassword
from sources.popup_message import error_popup
from sources.settings import SETTINGS
from uuid import UUID


class KeePassException(Exception):
    def __init__(self, message):
        super().__init__(message)


class KeePassField(Enum):
    TITLE = 'title'
    USERNAME = 'username'
    PASSWORD = 'password'


def database_required(func):
    def wrapper(self, *args, **kwargs):
        if not self.database:
            raise KeePassException('KeePass not loaded')
        return func(self, *args, **kwargs)

    return wrapper


class KeePass:
    def __init__(self):
        self.master_key: Optional[str] = None
        self.database: Optional[PyKeePass] = None
        self.group: Optional[Group] = None

    def load(self):
        if self.database is not None:
            return

        if not SETTINGS.keepass_enabled:
            return

        if not SETTINGS.keepass_path:
            return

        if not os.path.exists(SETTINGS.keepass_path):
            SETTINGS.keepass_enabled = False
            SETTINGS.keepass_path = ''
            SETTINGS.save()
            return

        max_tries = 3
        tries = 0
        error_message = ''
        while tries < max_tries:
            try:
                if not self.master_key:
                    self.master_key = get_password(message='Enter KeePass master key:', error_message=error_message)
                self.database = PyKeePass(SETTINGS.keepass_path, password=self.master_key)
                self.group = self.database.find_groups_by_name(APP_TITLE, first=True)
                return
            except CredentialsError:
                self.master_key = None
                error_message = f'Invalid master key. {max_tries - tries - 1} attempt{"" if max_tries - tries - 1 == 1 else "s"} left.'
                tries += 1

        raise KeePassException('Invalid master key')

    def create(self) -> str:
        if os.path.exists(KEEPASS_CREATE_PATH):
            raise KeePassException('KeePass file already exists')

        try:
            self.master_key = get_password(message='Enter KeePass master key:')
        except InvalidPassword:
            error_popup('Invalid master key')
            return ''

        self.database = create_database(KEEPASS_CREATE_PATH, password=self.master_key)
        self.group = self.database.add_group(self.database.root_group, APP_TITLE, icon='1')
        self.database.save()

        return KEEPASS_CREATE_PATH

    @database_required
    def add_account(self, account: Account):
        try:
            self.database.add_entry(self.group, account.title, account.username, account.password, icon='1')
            self.database.save()
        except Exception as e:
            raise KeePassException(f'Account  already exists:\nTitle: {account.title}\nUsername: {account.username}')

    def get_entry(self, account_id: str) -> Entry:
        return self.database.find_entries(uuid=UUID(account_id), first=True)

    @database_required
    def get_account(self, account_id: str) -> Account:
        entry = self.get_entry(account_id=account_id)
        return Account(account_id=str(entry.uuid), title=entry.title, username=entry.username, password=entry.password)

    @database_required
    def update_account_field(self, account_id: str, field: KeePassField, value: str):
        entry = self.get_entry(account_id=account_id)
        entry.__setattr__(field.value, value)
        self.database.save()

    @database_required
    def delete_account(self, account_id: str):
        entry = self.get_entry(account_id=account_id)
        self.database.delete_entry(entry)
        self.database.save()

    def list_accounts(self):
        if not self.group:
            return []
        return [Account(account_id=str(entry.uuid), title=entry.title, username=entry.username, password=entry.password) for entry in self.group.entries]


KEEPASS: KeePass = KeePass()
