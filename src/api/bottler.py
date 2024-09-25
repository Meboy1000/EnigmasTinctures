from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db


router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)


    
class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_bottles(potions_delivered: list[PotionInventory], order_id: int):
    """ """
    with db.engine.begin() as connection:
        inventory = connection.execute(sqlalchemy.text(SELECT * FROM global_inventory))
        inventory[2] += potions_delivered[0].quantity
        inventory[3] -= potions_delivered[0].quantity*100
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_potions = inventory[2], num_green_ml = inventory[3]"))
    print(f"potions delievered: {potions_delivered} order_id: {order_id}")
    
    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.
    with db.engine.begin() as connection:
        inventory = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
    # Updated logic: bottle all barrels into green potions. Do not bottle if out of ml

    return [
            {
                "potion_type": [0, 100, 0, 0],
                "quantity": (inventory[3]//100),
            }
        ]

if __name__ == "__main__":
    print(get_bottle_plan())
