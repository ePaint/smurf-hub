import sys
from definitions import APP_MANAGER
from sources.app import AppSource
from sources.main_window import MainWindow


def start_app():
    window = MainWindow()
    window.start_app()
    APP_MANAGER.start(AppSource.MAIN_WINDOW)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


def main():
    sys.excepthook = except_hook
    start_app()


if __name__ == "__main__":
    main()
