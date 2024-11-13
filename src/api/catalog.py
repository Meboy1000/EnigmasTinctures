from fastapi import APIRouter
import sqlalchemy
from src import database as db
from .utils import inv
router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
    catalog = []
    potion_log = inv.get_potions_catalog()

    for potion in potion_log:
        if potion.quantity != 0:
            catalog.append(
                {
                    "sku": potion.sku,
                    "name": potion.name,
                    "quantity": potion.quantity,
                    "price": potion.price,
                    "potion_type" : potion.recipe,

                }
            )
    catalog = catalog[:6]
    return catalog
