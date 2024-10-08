from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import math  # noqa: F401
import sqlalchemy
from src import database as db
from .utils import inv
router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/audit")
def get_inventory():
    """ """ 
    # final inventory read logic, will work in perpetuity. check for security later.
    total_ml = 0
    ml = inv.get_ml()
    for num in ml:
        total_ml += num
    return {"number_of_potions": inv.get_num_potions(), "ml_in_barrels": total_ml, "gold": inv.get_gold()}

# Gets called once a day
@router.post("/plan")
def get_capacity_plan():
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """
    gold = inv.get_gold()
    num_pots = inv.get_num_potions()
    pot_cap = inv.get_potion_cap()
    if num_pots > (pot_cap//4 * 3) and gold > 1100:
        return {
        "potion_capacity": 1,
        "ml_capacity": 0
        }
    num_ml = inv.get_ml()
    ml_cap = inv.get_ml_cap()
    if num_ml > (ml_cap//4 * 3) and gold > 1100:
        return {
        "potion_capacity": 0,
        "ml_capacity": 1
        }
    
    return {
        "potion_capacity": 0,
        "ml_capacity": 0
        }

class CapacityPurchase(BaseModel):
    potion_capacity: int
    ml_capacity: int

# Gets called once a day
@router.post("/deliver/{order_id}")
def deliver_capacity_plan(capacity_purchase : CapacityPurchase, order_id: int):
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """


    return "OK"
