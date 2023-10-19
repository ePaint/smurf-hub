import argparse
import sys
from definitions import APP_MANAGER
from sources.keepass import KEEPASS
from sources.app import AppSource
from sources.lol_manager import login_lol_client
from sources.main_window import MainWindow


def start_app():
    window = MainWindow()
    window.start_app()
    APP_MANAGER.start(AppSource.MAIN_WINDOW)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


def main():
    sys.excepthook = except_hook

    parser = argparse.ArgumentParser()
    parser.add_argument('--account-id', required=False, help='The account_id of the account to login')
    args = parser.parse_args()
    KEEPASS.load()

    if args.account_id:
        login_lol_client(account_id=str(args.account_id))
    else:
        start_app()


if __name__ == "__main__":
    main()
