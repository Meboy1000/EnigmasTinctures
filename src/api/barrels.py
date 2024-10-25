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
    print(gold)
    # skip unnecessary logic if gold too low
    if gold < 100:
        print("No Barrels")
        return[]
    
    inventory = inv.get_ml()
    # basic bootstrap
    if gold < 400:
        if inventory[1] == 0 and gold >= 100:
            plan.append({
                "sku": "SMALL_GREEN_BARREL",
                "quantity": 1,
            })
            gold -= 100
        if inventory[0] == 0 and gold >= 100:
            plan.append({
                "sku": "SMALL_RED_BARREL",
                "quantity": 1,
            })
            gold -= 100
        if inventory[2] == 0 and gold >= 120:
            plan.append({
                "sku": "SMALL_BLUE_BARREL",
                "quantity": 1,
            })
        print(plan)
        return plan
        

    # rearrange catalog for easier logic
    catalog = tools.organizeCatalog(wholesale_catalog)
    
    # distribute goals and budget
    goal_ml = inv.get_ml_cap()/4
    needed = [goal_ml-inventory[0], goal_ml-inventory[1], goal_ml-inventory[2], goal_ml-inventory[3]]
    total_need = sum(needed)
    percents = [(needed[0]/total_need), (needed[1]/total_need), (needed[2]/total_need), (needed[3]/total_need)]
    budget = [gold*percents[0], gold*percents[1], gold*percents[2], gold*percents[3], 0]

    # redistributes budget if unable to afford anything dark
    if budget[3] < 750:
        budget = [i + budget[3]//3 for i in budget]
        budget[3] = 0 
        needed = [i + needed[3]//4 for i in needed] # keeps buffer but allows ml to go above capacity purchase threshold
        needed[3] = 0 
    # for each type of ingredient
    for x in range(4):
        # for each barrel of said type, in order from largest to smallest
        for barrel in catalog[x]:
            # avoids not offered barrels
            if barrel.price != 0:
                # gets the most of a barrel affordable or purchasable that does not exceed the desired ml
                affordable = int(min(budget[x] // barrel.price, barrel.quantity, needed[x]//barrel.ml_per_barrel))
                if affordable != 0:
                    plan.append({
                        "sku": barrel.sku,
                        "quantity": affordable,
                    })
                budget[x] -= barrel.price*affordable
                needed[x] -= barrel.ml_per_barrel*affordable
        # roll extra gold to the next ml type
        budget[x+1] += budget[x]
    print(plan)
    return plan