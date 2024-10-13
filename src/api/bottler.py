from operator import add
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
    inv.update_potions_list(potions_delivered)
    ml_update = [0,0,0,0]
    for potions in potions_delivered:
        update = [x*(potions.quantity)*-1 for x in potions.potion_type]
        ml_update = list(map(add, update, ml_update))
    inv.update_ml_full(ml_update)
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
    capacity = inv.get_potion_cap
    for potion in catalog:
        quantity = capacity
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
            capacity -= quantity


    return plan

if __name__ == "__main__":
    print(get_bottle_plan())
