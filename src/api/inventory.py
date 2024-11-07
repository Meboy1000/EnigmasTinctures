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
    return {"number_of_potions": inv.get_num_potions(),
            "ml_in_barrels": inv.get_ml_sum(), 
            "gold": inv.get_gold()}

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
    num_ml = inv.get_ml_sum()
    ml_cap = inv.get_ml_cap()
    if (ml_cap/10000) > 10 and (pot_cap/50) > 15:
        return {
        "potion_capacity": 0,
        "ml_capacity": 0
        }
    if gold > (ml_cap//7):
        gold_use = max((gold-(ml_cap//8)), min(gold-(((ml_cap//10000)-(pot_cap//50))*1000), (gold//2)))//1000
        des_pcap = min((gold_use//2), max(0, (15-(pot_cap//50))))
        des_mcap = min(-(gold_use//(-2)), max(0, 10-(ml_cap//10000)))
        if gold_use != 0:
            return{
            "potion_capacity": des_pcap,
            "ml_capacity": des_mcap    
            }
    if num_pots > ((pot_cap//4) * 3) and gold >= 1100:
        return {
        "potion_capacity": 1,
        "ml_capacity": 0
        }
    
    if num_ml > ((ml_cap//4) * 3) and gold >= 1100:
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
    inv.update_capacity(capacity_purchase.ml_capacity, capacity_purchase.potion_capacity)
    inv.update_gold((-1000)*(capacity_purchase.ml_capacity + capacity_purchase.potion_capacity))

    return "OK"
