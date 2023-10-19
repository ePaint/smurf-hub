import os
import sys
from pathlib import Path
from sources.app import AppManager

APP_MANAGER: AppManager = AppManager()
APP_TITLE = 'Smurf Hub'
EXEC_FOLDER = Path(os.path.dirname(sys.executable))
EXEC_PATH = str(EXEC_FOLDER.joinpath(f'{APP_TITLE}.exe'))
PROJECT_FOLDER = Path(os.path.dirname(os.path.abspath(__file__)))
PAYPAL_IMAGE_PATH = str(PROJECT_FOLDER.joinpath('paypal.png'))
PAYPAL_DONATE_URL = 'https://www.paypal.com/donate/?hosted_button_id=ASL33HJH2PR98'
SETTINGS_PATH = str(EXEC_FOLDER.joinpath('settings.json'))
ACCOUNTS_PATH = str(EXEC_FOLDER.joinpath('accounts.json'))
VBS_FOLDER = EXEC_FOLDER.joinpath('utils')
UI_FOLDER = PROJECT_FOLDER.joinpath('ui')
ICON_PATH = str(UI_FOLDER.joinpath('icon.ico'))
ICON_ERROR_PATH = str(UI_FOLDER.joinpath('icon_error.ico'))
MAIN_UI_PATH = str(UI_FOLDER.joinpath('main.ui'))
PASSWORD_UI_PATH = str(UI_FOLDER.joinpath('password.ui'))
MESSAGE_UI_PATH = str(UI_FOLDER.joinpath('message.ui'))
PYTHON_VENV_PATH = str(PROJECT_FOLDER.joinpath('venv').joinpath('Scripts').joinpath('python.exe'))
LOL_MANAGER_PATH = str(PROJECT_FOLDER.joinpath('lol_manager.py'))
DESKTOP_PATH = Path.home().joinpath('Desktop')
