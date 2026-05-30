from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Identity, Index, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class MasterData(Base):
    __tablename__ = "master_data_config"
    __table_args__ = (
        UniqueConstraint("category_name", "code", name="uq_master_data_config_category_code"),
        Index("ix_master_data_config_category", "category_name"),
        Index("ix_master_data_config_parent", "parent_category_name", "parent_code"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=False), primary_key=True)
    category_name: Mapped[str] = mapped_column(String(100), nullable=False)
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str] = mapped_column(String(100), nullable=False)
    parent_category_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    parent_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    sort_order: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
