from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_session
from app.models import MasterData
from app.schemas.common import MasterData as MasterDataSchema

router = APIRouter(prefix="/master-data", tags=["master-data"])


@router.get("", response_model=list[MasterDataSchema])
def list_master_data(
    session: Annotated[Session, Depends(get_session)],
    category: Annotated[str | None, Query(min_length=1, max_length=100)] = None,
    parent_code: Annotated[str | None, Query(min_length=1, max_length=100)] = None,
    include_inactive: bool = False,
) -> list[MasterDataSchema]:
    statement = select(MasterData).order_by(MasterData.sort_order, MasterData.display_name)
    if category:
        statement = statement.where(MasterData.category_name == category)
    if parent_code:
        statement = statement.where(MasterData.parent_code == parent_code)
    if not include_inactive:
        statement = statement.where(MasterData.is_active.is_(True))

    rows = session.scalars(statement).all()
    return [
        MasterDataSchema(
            category_name=row.category_name,
            display_name=row.display_name,
            code=row.code,
            parent_category_name=row.parent_category_name,
            parent_code=row.parent_code,
            sort_order=row.sort_order,
            is_active=row.is_active,
        )
        for row in rows
    ]
