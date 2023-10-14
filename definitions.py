import os
from pathlib import Path
from sources.app import AppManager


APP_MANAGER = AppManager()
APP_TITLE = 'Smurf Hub'
PROJECT_FOLDER = Path(os.path.dirname(os.path.abspath(__file__)))
ICON_PATH = str(PROJECT_FOLDER.joinpath('icon.ico'))
SETTINGS_PATH = str(PROJECT_FOLDER.joinpath('settings.json'))
ACCOUNTS_PATH = str(PROJECT_FOLDER.joinpath('accounts.json'))
MAIN_UI_PATH = str(PROJECT_FOLDER.joinpath('ui').joinpath('main.ui'))
PASSWORD_UI_PATH = str(PROJECT_FOLDER.joinpath('ui').joinpath('password.ui'))
MESSAGE_UI_PATH = str(PROJECT_FOLDER.joinpath('ui').joinpath('message.ui'))
PYTHON_VENV_PATH = str(PROJECT_FOLDER.joinpath('venv').joinpath('Scripts').joinpath('python.exe'))
LOL_MANAGER_PATH = str(PROJECT_FOLDER.joinpath('lol_manager.py'))
DESKTOP_PATH = Path.home().joinpath('Desktop')
