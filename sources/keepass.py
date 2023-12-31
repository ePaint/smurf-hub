import os
import subprocess
from enum import Enum
from typing import Optional
from pykeepass.pykeepass import BLANK_DATABASE_PASSWORD
from sources.popup import popup_get_password
from sources.settings import SETTINGS
from pykeepass import PyKeePass
from pykeepass.entry import Entry
from pykeepass.exceptions import CredentialsError
from pykeepass.group import Group
from definitions import APP_TITLE, KEEPASS_CREATE_PATH, KEEPASS_TEMPLATE_PATH
from sources.accounts import Account
from uuid import UUID
from cryptography.fernet import Fernet


MASTER_KEY_ENV_VAR = 'SMURF_HUB_KEEPASS_MASTER_KEY'
SECRET_KEY_ENV_VAR = 'SMURF_HUB_KEEPASS_SECRET_KEY'


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
        self.secret_key: Optional[str] = os.environ.get(SECRET_KEY_ENV_VAR)
        print(f'KeePass secret key: {self.secret_key}')
        if not self.secret_key:
            self.secret_key = Fernet.generate_key().decode('utf-8')
            self._save_to_env(SECRET_KEY_ENV_VAR, self.secret_key)

        self.master_key: Optional[str] = None
        self.database: Optional[PyKeePass] = None
        self.group: Optional[Group] = None

        self.load_master_key_from_env()

        print(f'KeePass secret key: {self.secret_key}')
        print(f'KeePass master key: {self.master_key}')

    def load(self):
        if self.database is not None:
            return

        if not SETTINGS.keepass_path:
            return

        if not os.path.exists(SETTINGS.keepass_path):
            SETTINGS.keepass_path = ''
            SETTINGS.save()
            return

        max_tries = 3
        tries = 0
        error_message = ''
        while tries < max_tries:
            try:
                if not self.master_key:
                    self.master_key, submitted = popup_get_password(error_message=error_message)
                    if not submitted:
                        raise KeePassException('KeePass not loaded')
                self.database = PyKeePass(SETTINGS.keepass_path, password=self.master_key)
                for group in self.database.root_group.subgroups:
                    if group.name == APP_TITLE:
                        self.group = group
                        return
                self.group = self.database.add_group(self.database.root_group, APP_TITLE, icon='1')
                self.database.save()
                return
            except CredentialsError:
                self.master_key = None
                error_message = f'Invalid master key. {max_tries - tries - 1} attempt{"" if max_tries - tries - 1 == 1 else "s"} left.'
                tries += 1

        raise KeePassException('Invalid master key')

    def unload(self, keep_master_key: bool = False):
        if not keep_master_key:
            self.master_key = None
        self.database = None
        self.group = None

    def reload(self, keep_master_key: bool = False):
        if self.database.filename == SETTINGS.keepass_path:
            self.load()
            return

        previous_master_key = self.master_key
        previous_database = self.database
        previous_group = self.group
        self.unload(keep_master_key=keep_master_key)
        try:
            self.load()
        except KeePassException as e:
            self.master_key = previous_master_key
            self.database = previous_database
            self.group = previous_group
            raise e

    def create(self) -> str:
        if os.path.exists(KEEPASS_CREATE_PATH):
            return KEEPASS_CREATE_PATH

        self.master_key, submitted = popup_get_password()
        if not submitted:
            raise KeePassException('KeePass not created')

        try:
            print(f'Creating KeePass file: {KEEPASS_CREATE_PATH}')
            print(f'KeePass master key: {self.master_key}')
            print(f'KeePass template: {KEEPASS_TEMPLATE_PATH}')
            self.database = PyKeePass(KEEPASS_TEMPLATE_PATH, BLANK_DATABASE_PASSWORD)
            self.database.filename = KEEPASS_CREATE_PATH
            self.database.password = self.master_key
            self.group = self.database.add_group(self.database.root_group, APP_TITLE, icon='1')
            self.database.save()
        except Exception:
            raise KeePassException('Failed to create KeePass file')

        return KEEPASS_CREATE_PATH

    def save_master_key_to_env(self):
        print(f'Encrypting master key: {self.master_key}')
        encrypted_master_key = Fernet(self.secret_key.encode('utf-8')).encrypt(self.master_key.encode('utf-8'))
        decoded_encrypted_master_key = encrypted_master_key.decode('utf-8')
        self._save_to_env(MASTER_KEY_ENV_VAR, decoded_encrypted_master_key)

    def load_master_key_from_env(self):
        print(f'Decrypting master key')
        encrypted_master_key = os.environ.get(MASTER_KEY_ENV_VAR)
        if not encrypted_master_key:
            return
        self.master_key = Fernet(self.secret_key.encode('utf-8')).decrypt(encrypted_master_key.encode('utf-8')).decode('utf-8')

    def remove_master_key_from_env(self):
        print(f'Removing master key')
        if MASTER_KEY_ENV_VAR in os.environ:
            del os.environ[MASTER_KEY_ENV_VAR]
            self._save_to_env(MASTER_KEY_ENV_VAR, '')

    @staticmethod
    def _save_to_env(key, value):
        os.environ[key] = value
        try:
            subprocess.run(['setx', key, value], check=True, capture_output=True, text=True, shell=True)
            print(f'Successfully set the environment variable: {key}={value}')
        except subprocess.CalledProcessError as e:
            raise KeePassException(f'Error setting the environment variable: {e.stderr}')

    @database_required
    def add_account(self, account: Account):
        try:
            self.database.add_entry(self.group, account.title, account.username, account.password, icon='1')
            self.database.save()
        except Exception:
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
