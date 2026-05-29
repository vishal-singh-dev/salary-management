from sqlalchemy import Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class MasterData(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "master_data"
    __table_args__ = (
        UniqueConstraint("category", "value", name="uq_master_data_category_value"),
        UniqueConstraint("category", "description", name="uq_master_data_category_description"),
        Index("ix_master_data_category", "category"),
    )

    category: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str] = mapped_column(String(200), nullable=False)
    value: Mapped[str] = mapped_column(String(80), nullable=False)
