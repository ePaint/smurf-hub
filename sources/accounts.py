import os
from enum import Enum
from typing import List, Optional, Dict
from pydantic import BaseModel, Field, validator, root_validator
from definitions import PROJECT_FOLDER


ACCOUNTS_PATH = str(PROJECT_FOLDER.joinpath('accounts.json'))


class KeepassStatus(Enum):
    NOT_SET = 0
    DISABLED = 1
    ENABLED = 2


class Account(BaseModel):
    name: str = None
    keepass: KeepassStatus = Field(default=KeepassStatus.NOT_SET, repr=False, exclude=True)
    keepass_reference: str = None
    username: str = None
    password: str = None

    @root_validator(pre=True)
    def root_validator(cls, values):
        keepass_enabled = values.get('keepass_enabled')
        if keepass_enabled is True:
            values['keepass'] = KeepassStatus.ENABLED
        elif keepass_enabled is False:
            values['keepass'] = KeepassStatus.DISABLED
        else:
            values['keepass'] = KeepassStatus.NOT_SET
        return values

    @validator('keepass_reference')
    def keepass_reference_validator(cls, v, values):
        if values['keepass'] == KeepassStatus.ENABLED and not v:
            raise ValueError('keepass_reference must be set if keepass_enabled is True')
        return v

    @validator('username')
    def username_validator(cls, v, values):
        if values['keepass'] == KeepassStatus.DISABLED and not v:
            raise ValueError('username must be set if keepass_enabled is False')
        return v

    @validator('password')
    def password_validator(cls, v, values):
        if values['keepass'] == KeepassStatus.DISABLED and not v:
            raise ValueError('password must be set if keepass_enabled is False')
        return v


class Accounts(BaseModel):
    accounts: Dict[str, Account] = Field(default_factory=dict)

    def add(self, account: Account):
        self.accounts[account.name] = account

    def get_account(self, name: str) -> Optional[Account]:
        return self.accounts.get(name)

    def save(self):
        print(self.json(indent=4, exclude_none=True))
        with open(ACCOUNTS_PATH, 'w+') as f:
            f.write(self.json(indent=4, exclude_none=True))
        print('finished saving')

    def delete(self, index: int):
        account = list(self.accounts.values())[index]
        del self.accounts[account.name]

    def clear(self):
        self.accounts = {}
        self.save()


try:
    ACCOUNTS: Accounts = Accounts.parse_raw(open(ACCOUNTS_PATH, 'r+').read())
except FileNotFoundError as e:
    ACCOUNTS: Accounts = Accounts()
