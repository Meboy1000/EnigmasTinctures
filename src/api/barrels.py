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
        cost = inventory[4] - (barrels_delivered[0].price*barrels_delivered[0].quantity)
        newml = inventory[3] + (barrels_delivered[0].ml_per_barrel*barrels_delivered[0].quantity)
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_ml = " + str(newml) + ", gold = " + str(cost)))
    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    with db.engine.begin() as connection:
        num_pots = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory")).first()[0]
            
    return [
        {
            "sku": "SMALL_GREEN_BARREL",
            "quantity": 1 if num_pots < 10 else 0,
        }
    ]

