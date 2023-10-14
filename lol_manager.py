import argparse
import psutil
from enum import Enum
from time import sleep
from pykeepass import PyKeePass
from pykeepass.exceptions import CredentialsError
from pynput.keyboard import Key, Controller
from sources.accounts import ACCOUNTS, Account
from sources.popup_message import error_popup
from sources.password_popup import get_password
from sources.settings import SETTINGS


class InvalidSettings(Exception):
    def __init__(self, message):
        super().__init__(message)


class InvalidAccount(Exception):
    def __init__(self, message):
        super().__init__(message)


class InvalidCredentials(Exception):
    def __init__(self, message):
        super().__init__(message)


class LoginBehavior(Enum):
    USE_SETTINGS = 'use_settings'  # Check settings to see if keepass should be used (default)
    ALWAYS_USE_KEEPASS = 'always_use_keepass'
    NEVER_USE_KEEPASS = 'never_use_keepass'


def get_account(name: str) -> Account:
    account: Account = ACCOUNTS.get_account(name)
    if not account:
        raise InvalidAccount(f'Account "{name}" not found')
    return account


def get_credentials(account: Account, behavior: LoginBehavior = LoginBehavior.USE_SETTINGS) -> (str, str):
    if behavior == LoginBehavior.ALWAYS_USE_KEEPASS:
        use_keepass = True
    elif behavior == LoginBehavior.NEVER_USE_KEEPASS:
        use_keepass = False
    else:
        use_keepass = SETTINGS.keepass_enabled

    print(f'get_credentials: use_keepass = {use_keepass}')
    if use_keepass:
        if not SETTINGS.keepass_path:
            raise InvalidCredentials('KeePass path not set')

        if not account.keepass_reference:
            raise InvalidCredentials('KeePass reference not set')

        master_key = get_password()
        try:
            keepass = PyKeePass(SETTINGS.keepass_path, password=master_key)
        except CredentialsError:
            raise InvalidCredentials('Invalid master key')

        entry = keepass.find_entries(title=account.keepass_reference, first=True)
        username, password = entry.username, entry.password
    else:
        username, password = account.username, account.password

    if not username or not password:
        raise InvalidCredentials('Username or password not set')

    return username, password


def stop_lol_client():
    if not SETTINGS.lol_path:
        raise InvalidSettings('League of Legends path not set')

    if not SETTINGS.lol_process_names:
        raise InvalidSettings('League of Legends process names not set')

    for process in psutil.process_iter():
        if process.name() in SETTINGS.lol_process_names:
            process.terminate()


def start_lol_client():
    if not SETTINGS.lol_path:
        raise InvalidSettings('League of Legends path not set')

    from pywinauto import Application, Desktop

    try:
        Application(backend='uia').start(SETTINGS.lol_client_path + ' ' + SETTINGS.lol_client_args)
    except Exception:
        raise InvalidSettings(f'Invalid League of Legends path')

    return Desktop(backend='uia').window(title_re='.*Riot Client Main.*')


def restart_lol_client():
    stop_lol_client()
    return start_lol_client()


def login_lol_client(name: str, behavior: LoginBehavior = LoginBehavior.USE_SETTINGS):
    print(f'Logging in {name}, behavior = {behavior}')

    try:
        account = get_account(name)
    except InvalidAccount as e:
        print(e)
        error_popup(message=str(e))
        return
    try:
        username, password = get_credentials(account, behavior)
    except (InvalidAccount, InvalidCredentials) as e:
        print(e)
        error_popup(message=str(e))
        return

    try:
        window = restart_lol_client()
    except InvalidSettings as e:
        print(e)
        error_popup(message=str(e))
        return

    for i in range(20):
        if window.exists():
            break
        print('Waiting for Riot Client Main window to appear')
        sleep(0.1)

    if not window.exists():
        message = 'Riot Client Main window not found'
        print(message)
        error_popup(message=message)
        return

    window.set_focus()
    keyboard = Controller()
    keyboard.type(username)
    keyboard.tap(Key.tab)
    keyboard.type(password)
    keyboard.tap(Key.tab)
    keyboard.tap(Key.tab)
    keyboard.tap(Key.tab)
    keyboard.tap(Key.tab)
    keyboard.tap(Key.tab)
    keyboard.tap(Key.tab)
    keyboard.tap(Key.enter)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', required=True, help='The name of the account to login')
    parser.add_argument('--behavior', required=False, help='Valid values = [use_keepass, use_settings, never_use_keepass]')
    args = parser.parse_args()
    login_lol_client(name=str(args.name), behavior=LoginBehavior(args.behavior))


if __name__ == "__main__":
    main()
