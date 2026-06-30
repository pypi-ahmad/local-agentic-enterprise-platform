from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    roles: list[str]


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    password: str = Field(min_length=8)
    role: str = "viewer"


class UserView(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    username: str
    full_name: str
    role: str
