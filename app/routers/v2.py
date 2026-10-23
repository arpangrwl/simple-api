"""Version 2: adds a category to items, plus filtering by category."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app import store
from app.auth.deps import require_role

router = APIRouter()


class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)
    category: str = Field("general", min_length=1)


class Item(BaseModel):
    id: int
    name: str
    price: float
    category: str


@router.get("/items", response_model=list[Item])
def list_items(category: str | None = None):
    return store.all_items(category)


@router.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int):
    item = store.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.post(
    "/items",
    status_code=201,
    response_model=Item,
    dependencies=[Depends(require_role("admin"))],  # only admins can create
)
def create_item(payload: ItemCreate):
    return store.add(payload.name, payload.price, payload.category)
