"""In-memory storage shared by every API version."""

_items: dict[int, dict] = {}
_next_id = 1


def add(name: str, price: float, category: str = "general") -> dict:
    global _next_id
    item = {"id": _next_id, "name": name, "price": price, "category": category}
    _items[_next_id] = item
    _next_id += 1
    return item


def get(item_id: int) -> dict | None:
    return _items.get(item_id)


def all_items(category: str | None = None) -> list[dict]:
    items = list(_items.values())
    if category is not None:
        items = [i for i in items if i["category"] == category]
    return items


def reset() -> None:
    global _next_id
    _items.clear()
    _next_id = 1
