from datetime import datetime
from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4

class BaseModel(SQLModel):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    is_active: bool = Field(default=True, nullable=False)

    async def pre_save(self) -> None:
        """Hook before saving"""
        self.updated_at = datetime.utcnow()

    async def pre_update(self) -> None:
        """Hook before updating"""
        self.updated_at = datetime.utcnow()

    async def pre_delete(self) -> None:
        """Hook before deletion"""
        pass
