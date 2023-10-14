import argparse
import sys
from definitions import APP_MANAGER
from sources.app import AppSource
from sources.lol_manager import login_lol_client, LoginBehavior
from sources.main_window import MainWindow


def start_app():
    APP_MANAGER.start(AppSource.MAIN_WINDOW)
    window = MainWindow()
    window.start_app()


def login(name: str, behavior: LoginBehavior = LoginBehavior.USE_SETTINGS):
    APP_MANAGER.start(AppSource.PASSWORD_POPUP)
    login_lol_client(name=name, behavior=behavior)
    APP_MANAGER.stop()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


def main():
    sys.excepthook = except_hook

    parser = argparse.ArgumentParser()
    parser.add_argument('--name', required=False, help='The name of the account to login')
    parser.add_argument('--behavior', required=False, help='Valid values = [use_keepass, use_settings, never_use_keepass]')
    args = parser.parse_args()

    if args.name:
        name = str(args.name)
        behavior = LoginBehavior(args.behavior) if args.behavior else LoginBehavior.USE_SETTINGS
        login(name=name, behavior=behavior)
    else:
        start_app()


if __name__ == "__main__":
    main()
