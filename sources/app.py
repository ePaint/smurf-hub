import sys
from enum import Enum

from PyQt6.QtWidgets import QApplication


class AppSource(Enum):
    MAIN_WINDOW = 'main_window'
    PASSWORD_POPUP = 'password_popup'


class AppManager:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.source = None
        self.is_running = False

    def start(self, source: AppSource):
        print('Starting app, source:', source)
        self.source = source
        self.is_running = True
        self.app.exec()

    def stop(self):
        print('Stopping app')
        self.source = None
        self.is_running = False
        self.app.quit()
        print('App stopped')
        print('is_running:', self.is_running)
        print('source:', self.source)
