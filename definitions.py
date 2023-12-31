import os
import sys
from pathlib import Path
from sources.app import AppManager

APP_MANAGER: AppManager = AppManager()
APP_TITLE = 'Smurf Hub'
EXEC_FOLDER = Path(os.path.dirname(sys.executable))
PROJECT_FOLDER = Path(os.path.dirname(os.path.abspath(__file__)))
PAYPAL_DONATE_URL = 'https://www.paypal.com/donate/?hosted_button_id=ASL33HJH2PR98'
EXEC_PATH = str(EXEC_FOLDER.joinpath(f'{APP_TITLE}.exe'))
KEEPASS_CREATE_PATH = str(EXEC_FOLDER.joinpath(f'{APP_TITLE}.kdbx'))
SETTINGS_PATH = str(EXEC_FOLDER.joinpath('settings.json'))
ACCOUNTS_PATH = str(EXEC_FOLDER.joinpath('accounts.json'))
UTILS_FOLDER = EXEC_FOLDER.joinpath('utils')
KEEPASS_TEMPLATE_PATH = str(PROJECT_FOLDER.joinpath('blank_database.kdbx'))
UI_FOLDER = PROJECT_FOLDER.joinpath('ui')
PAYPAL_IMAGE_PATH = str(UI_FOLDER.joinpath('paypal.png'))
ICON_PATH = str(UI_FOLDER.joinpath('icon.ico'))
ICON_ERROR_PATH = str(UI_FOLDER.joinpath('icon_error.ico'))
MAIN_UI_PATH = str(UI_FOLDER.joinpath('main.ui'))
PASSWORD_UI_PATH = str(UI_FOLDER.joinpath('password.ui'))
MESSAGE_UI_PATH = str(UI_FOLDER.joinpath('message.ui'))
PYTHON_VENV_PATH = str(PROJECT_FOLDER.joinpath('venv').joinpath('Scripts').joinpath('python.exe'))
LOL_MANAGER_PATH = str(PROJECT_FOLDER.joinpath('lol_manager.py'))
DESKTOP_PATH = Path.home().joinpath('Desktop')
