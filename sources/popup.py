from sources.message import MessagePopup
from sources.password import PasswordPopup


def popup_info(message: str):
    MessagePopup().info(message=message)


def popup_error(message: str):
    MessagePopup().error(message=message)


def popup_get_password(error_message: str = ''):
    password_popup = PasswordPopup(error_message=error_message)
    password_popup.get_password()
    return password_popup.password, password_popup.submitted
