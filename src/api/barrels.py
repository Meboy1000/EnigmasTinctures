from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from .utils import inv, tools

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_barrels(barrels_delivered: list[Barrel], order_id: int):
    """ """
    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")
    ml_total = [0,0,0,0]
    cost = 0
    for barrel in barrels_delivered:
        ml_add = barrel.ml_per_barrel*barrel.quantity
        update_ml = [i * ml_add for i in barrel.potion_type]
        ml_total = [ml_total[i] + update_ml[i] for i in range(len(ml_total))]
        cost -= barrel.price*barrel.quantity
    inv.update_ml_full(tuple(ml_total))
    inv.update_gold(cost)
    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    plan = []
    print(wholesale_catalog)
    gold = inv.get_gold()
    if gold < 100:
        return[]
    if gold < 400:
        if inv.get_potions_sku("GREEN_POTION_0").quantity == 0 and gold > 100:
            plan.append({
                "sku": "SMALL_GREEN_BARREL",
                "quantity": 1,
            })
            gold -= 100
        if inv.get_potions_sku("RED_POTION_0").quantity == 0 and gold > 100:
            plan.append({
                "sku": "SMALL_RED_BARREL",
                "quantity": 1,
            })
            gold -= 100
        if inv.get_potions_sku("BLUE_POTION_0").quantity == 0 and gold > 120:
            plan.append({
                "sku": "SMALL_BLUE_BARREL",
                "quantity": 1,
            })
        return plan
        


    catalog = tools.organizeCatalog(wholesale_catalog)
        
    
    
    inventory = inv.get_ml()
    goal_ml = inv.get_ml_cap()/4
    needed = [goal_ml-inventory[0], goal_ml-inventory[1], goal_ml-inventory[2], goal_ml-inventory[3]]
    total_need = sum(needed)
    percents = [(needed[0]/total_need), (needed[1]/total_need), (needed[2]/total_need), (needed[3]/total_need)]
    budget = [gold*percents[0], gold*percents[1], gold*percents[2], gold*percents[3], 0]

    # redistributes budget if unable to afford anything dark
    if budget[3] < 750:
        budget[0] += budget[3]//3
        budget[1] += budget[3]//3
        budget[2] += budget[3]//3
        budget[3] = 0 

    for x in range(4):
        for barrel in catalog[x]:
            if barrel.price != 0:
                affordable = int(min(budget[x] // barrel.price, barrel.quantity, needed[x]//barrel.ml_per_barrel))
                plan.append({
                    "sku": barrel.sku,
                    "quantity": affordable,
                })
                budget[x] -= barrel.price*affordable
                needed[x] -= barrel.ml_per_barrel*affordable
        budget[x+1] += budget[x]
    print(plan)
    return plan

