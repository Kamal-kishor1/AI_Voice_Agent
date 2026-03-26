from pydantic import BaseModel, EmailStr, Field, field_validator


def _validate_password_strength(password: str) -> str:
    if len(password) < 12 or len(password) > 128:
        raise ValueError("Password must be between 12 and 128 characters.")
    if not any(char.isupper() for char in password):
        raise ValueError("Password must contain at least one uppercase letter.")
    if not any(char.islower() for char in password):
        raise ValueError("Password must contain at least one lowercase letter.")
    if not any(char.isdigit() for char in password):
        raise ValueError("Password must contain at least one digit.")
    if not any(not char.isalnum() for char in password):
        raise ValueError("Password must contain at least one special character.")
    return password


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str = Field(min_length=1, max_length=150)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return _validate_password_strength(value)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(min_length=20)


class GoogleAuthorizeRequest(BaseModel):
    redirect_uri: str
    code_challenge: str
    state: str


class GoogleExchangeRequest(BaseModel):
    code: str
    code_verifier: str
    redirect_uri: str | None = None


class OnboardingTokenExchangeRequest(BaseModel):
    provider: str = Field(default="google")
    code: str
    code_verifier: str
    redirect_uri: str | None = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, value: str) -> str:
        return _validate_password_strength(value)


class DeleteAccountRequest(BaseModel):
    confirmation: str
