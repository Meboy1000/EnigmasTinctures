from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db


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

    with db.engine.begin() as connection:
        inventory = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory")).first()
        num_pots = inventory[2]
        gold = inventory[4]
        price : int
        for barrel in wholesale_catalog:
            print (barrel)
            if barrel.sku == "SMALL_GREEN_BARREL":
                price = barrel.price
        if gold > price & num_pots < 10:
            return [
                {
                    "sku": "SMALL_GREEN_BARREL",
                    "quantity": 1,
                }
            ]
        return []

