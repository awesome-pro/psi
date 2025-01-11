from .base import BaseModel
from .user import User


class Problem(BaseModel):
    title: str
    description: str
    created_by: User
    status: str
    images: str | None
    video: str | None
    