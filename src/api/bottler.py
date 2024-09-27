from fastapi import APIRouter, Depends
from enum import Enum  # noqa: F401
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
    print("Delivered" + potions_delivered)
    with db.engine.begin() as connection:
        inventory = connection.execute(sqlalchemy.text("SELECT num_green_potions, num_green_ml FROM global_inventory")).first()
        newpots = inventory[0]
        new_green_ml = inventory[1]
        new_red_ml = 0
        new_blue_ml = 0
        new_dark_ml = 0
        for PotionInv in potions_delivered:
            newpots += PotionInv.quantity
            new_red_ml -= PotionInv.quantity * PotionInv.potion_type[0] 
            new_green_ml -= PotionInv.quantity * PotionInv.potion_type[1]
            new_blue_ml -= PotionInv.quantity * PotionInv.potion_type[2]
            new_dark_ml -= PotionInv.quantity * PotionInv.potion_type[3]
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_green_potions = {newpots}, num_green_ml = {new_green_ml}"))
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
        inventory = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory")).first()
    # Updated logic: bottle all barrels into green potions. Do not bottle if out of ml
        ml = inventory[3]
        quantity = ml//100
        if quantity > 0:
            return [
                    {
                        "potion_type": [0, 100, 0, 0],
                        "quantity": (quantity),
                    }
                ]
        return[]

if __name__ == "__main__":
    print(get_bottle_plan())
