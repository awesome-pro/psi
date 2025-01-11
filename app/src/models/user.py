from sqlmodel import Field, Relationship
from pydantic import EmailStr
from .base import BaseModel
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(BaseModel, table=True):
    __tablename__ = "users"

    email: EmailStr = Field(unique=True, index=True, nullable=False)
    hashed_password: str = Field(nullable=False)
    full_name: str = Field(max_length=100)
    role: str = Field(default="user")
    is_active: bool = Field(default=True)
    
    # Relationships can be added here
    # posts: List["Post"] = Relationship(back_populates="author")

    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    async def pre_save(self) -> None:
        await super().pre_save()
        # Add any additional pre-save logic here

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "full_name": "John Doe",
            }
        }
