from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from utils import inv, tools

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

    with db.engine.begin() as connection:
        inventory = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory")).first()    
        cost = inventory[4]
        newml = inventory[3]
        for barrel in barrels_delivered:
            cost -= barrel.price*barrel.quantity
            newml += barrel.ml_per_barrel*barrel.quantity
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_green_ml = {newml}, gold = {cost}"))
        print(newml)
        print(cost)
    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)
    gold = inv.get_gold()
    if gold < 100:
        return[]
    if gold < 400:
        if inv.get_potions_sku("GREEN_POTION_0").quantity == 0:
            return [{
                "sku": "SMALL_GREEN_BARREL",
                "quantity": 1,
            }]
        elif inv.get_potions_sku("RED_POTION_0").quantity == 0:
            return [{
                "sku": "SMALL_RED_BARREL",
                "quantity": 1,
            }]
        elif inv.get_potions_sku("BLUE_POTION_0").quantity == 0 and gold > 120:
            return [{
                "sku": "SMALL_BLUE_BARREL",
                "quantity": 1,
            }]
        


    catalog = tools.organizeCatalog(wholesale_catalog)
        
    plan = []
    
    inventory = inv.get_ml
    goal_ml = inv.get_ml_cap()/4
    needed = [goal_ml-inventory[0], goal_ml-inventory[1], goal_ml-inventory[2], goal_ml-inventory[3]]
    total_need = sum(needed)
    percents = [(needed[0]/total_need), (needed[1]/total_need), (needed[2]/total_need), (needed[3]/total_need)]
    budget = [gold*percents[0], gold*percents[1], gold*percents[2], gold*percents[3]]

    # redistributes budget if unable to afford anything dark
    if budget[3] < 750:
        budget[0] += budget[3]//3
        budget[1] += budget[3]//3
        budget[2] += budget[3]//3
        budget[3] = 0 

    for x in range(4):
        for barrel in catalog[x]:
            if barrel.price != 0:
                affordable = min(budget[x] // barrel.price, barrel.quantity, needed[x]//barrel.ml_per_barrel)
                plan.append[{
                    "sku": barrel.sku,
                    "quantity": affordable,
                }]
                budget[x] -= barrel.price*affordable
                needed[x] -= barrel.ml_per_barrel*affordable

    return plan

