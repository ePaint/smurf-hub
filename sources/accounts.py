from pydantic import BaseModel, Field, validator


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
