import psutil
import sys
from enum import Enum
from time import sleep
from pynput.keyboard import Key, Controller
from sources.accounts import Account
from sources.keepass import KEEPASS
from sources.popup_message import error_popup
from sources.settings import SETTINGS
import ctypes
ctypes.windll.ole32.CoInitialize()
sys.coinit_flags = 2
from pywinauto import Application, Desktop


class InvalidSettings(Exception):
    def __init__(self, message):
        super().__init__(message)


class InvalidAccount(Exception):
    def __init__(self, message):
        super().__init__(message)


class InvalidCredentials(Exception):
    def __init__(self, message):
        super().__init__(message)


def get_account(account_id: str) -> Account:
    KEEPASS.load()
    account: Account = KEEPASS.get_account(account_id=account_id)
    if not account:
        raise InvalidAccount(f'Account "{account_id}" not found')
    return account


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

    try:
        Application(backend='uia').start(SETTINGS.lol_client_path + ' ' + SETTINGS.lol_client_args)
    except Exception:
        raise InvalidSettings(f'Invalid League of Legends path')

    return Desktop(backend='uia').window(title_re='.*Riot Client Main.*')


def restart_lol_client():
    stop_lol_client()
    return start_lol_client()


def login_lol_client(account_id: str):
    print(f'Logging in {account_id}')

    try:
        account = get_account(account_id=account_id)
        print(f'Account: {account.json(indent=4)}')
    except InvalidAccount as e:
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

    sleep(2)

    window.set_focus()
    keyboard = Controller()
    keyboard.type(account.username)
    keyboard.tap(Key.tab)
    keyboard.type(account.password)
    keyboard.tap(Key.tab)
    keyboard.tap(Key.tab)
    keyboard.tap(Key.tab)
    keyboard.tap(Key.tab)
    keyboard.tap(Key.tab)
    keyboard.tap(Key.tab)
    keyboard.tap(Key.enter)
