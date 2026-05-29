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
    category: Annotated[str | None, Query(min_length=1, max_length=80)] = None,
) -> list[MasterDataSchema]:
    statement = select(MasterData).order_by(MasterData.category, MasterData.value)
    if category:
        statement = statement.where(MasterData.category == category)

    rows = session.scalars(statement).all()
    return [
        MasterDataSchema(
            category=row.category,
            description=row.description,
            value=row.value,
        )
        for row in rows
    ]
