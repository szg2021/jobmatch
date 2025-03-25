from typing import Optional

from pydantic import BaseModel

from app.schemas.user import User


class Token(BaseModel):
    access_token: str
    token_type: str
    user: Optional[User] = None


class TokenPayload(BaseModel):
    sub: Optional[str] = None 