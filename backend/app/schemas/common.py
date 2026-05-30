from pydantic import BaseModel, Field


class PaginationMeta(BaseModel):
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
    total_items: int = Field(ge=0)
    total_pages: int = Field(ge=0)


class MasterData(BaseModel):
    category_name: str
    display_name: str
    code: str
    parent_category_name: str | None = None
    parent_code: str | None = None
    sort_order: int | None = None
    is_active: bool
