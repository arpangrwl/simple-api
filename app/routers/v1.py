"""Version 1: items have id, name and price only."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app import store

router = APIRouter()


class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)


class Item(BaseModel):
    id: int
    name: str
    price: float


@router.get("/items", response_model=list[Item])
def list_items():
    return store.all_items()


@router.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int):
    item = store.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.post("/items", status_code=201, response_model=Item)
def create_item(payload: ItemCreate):
    return store.add(payload.name, payload.price)
