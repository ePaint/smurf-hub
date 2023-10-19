from enum import Enum
from typing import Optional, Dict
from pydantic import BaseModel, Field, validator, root_validator
from definitions import ACCOUNTS_PATH


class Account(BaseModel):
    account_id: str = None
    title: str = None
    username: str = None
    password: str = Field(default=None, exclude=True)

    @validator('title')
    def title_validator(cls, v):
        if not v:
            raise ValueError('Title must be set')
        return v

    @validator('username')
    def username_validator(cls, v):
        if not v:
            raise ValueError('Username must be set')
        return v

    @validator('password')
    def password_validator(cls, v):
        if not v:
            raise ValueError('Password must be set')
        return v


class Accounts(BaseModel):
    accounts: Dict[str, Account] = Field(default_factory=dict)

    def add(self, account: Account):
        self.accounts[account.title] = account

    def get_account(self, title: str) -> Optional[Account]:
        return self.accounts.get(title)

    def save(self):
        print(self.json(indent=4, exclude_none=True))
        with open(ACCOUNTS_PATH, 'w+') as f:
            f.write(self.json(indent=4, exclude_none=True))
        print('finished saving')

    def delete(self, index: int):
        account = list(self.accounts.values())[index]
        del self.accounts[account.title]

    def clear(self):
        self.accounts = {}
        self.save()


try:
    ACCOUNTS: Accounts = Accounts.parse_raw(open(ACCOUNTS_PATH, 'r+').read())
except FileNotFoundError as e:
    ACCOUNTS: Accounts = Accounts()
