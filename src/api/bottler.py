from fastapi import APIRouter, Depends
from enum import Enum  # noqa: F401
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from .utils import inv

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
    for potions in potions_delivered:
        potion = inv.get_potions_type(potions.potion_type)
        inv.update_potions(potion.sku, potions.quantity)
    print(f"potions delievered, order_id: {order_id}")
    
    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.
    plan = []
    catalog = inv.get_potions_catalog()
    ml_inv = inv.get_ml()
    for potion in catalog:
        quantity = inv.get_potion_cap()
        # temp logic, for pure color potions
        check = False
        for x in range(4):
            try:
                quantity = min(quantity, ml_inv[x]//potion.recipe[x])
                check = True
            except ZeroDivisionError:
                continue
        
        if quantity != 0 and check:
            plan.append(
                {
                    "potion_type" : potion.recipe,
                    "quantity" : quantity,
                }
            )


    return plan

if __name__ == "__main__":
    print(get_bottle_plan())
