from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import UserRole


class UserBase(BaseModel):
    # id: Mapped[int] = mapped_column(primary_key=True)
    # username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    # hashed_password: Mapped[str] = mapped_column(String(255))
    # role: Mapped[UserRole] = mapped_column(SqlEnum(UserRole, name="user_role",
    #                                                 values_callable=lambda enum_cls: [member.value for member in enum_cls]))
    # is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    username: str = Field(min_length=3, max_length=50)
    role: UserRole

class UserCreate(UserBase): # Hashing will be handled in router (remember think: format before being handled by code)
    password: str = Field(min_length=8)

class UserRead(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel): # Response format when sending token to client.
    access_token: str
    token_type: str = "bearer"