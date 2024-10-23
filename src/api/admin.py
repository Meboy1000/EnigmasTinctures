from fastapi import APIRouter, Depends, Request  # noqa: F401
from pydantic import BaseModel  # noqa: F401
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.post("/reset")
def reset():
    """
    Reset the game state. Gold goes to 100, all potions are removed from
    inventory, and all barrels are removed from inventory. Carts are all reset.
    """
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("DELETE FROM global_inventory"))
        connection.execute(sqlalchemy.text("INSERT INTO global_inventory (gold) VALUES (100)"))
        connection.execute(sqlalchemy.text("DELETE FROM capacity"))
        connection.execute(sqlalchemy.text("INSERT INTO capacity (ml_capacity, potion_capacity) VALUES (1, 1)"))
        connection.execute(sqlalchemy.text("DELETE FROM carts_log"))
        connection.execute(sqlalchemy.text("DELETE FROM cart_items"))
        connection.execute(sqlalchemy.text("DELETE FROM potion_inventory"))
    return "OK"

