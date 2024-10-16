from fastapi import APIRouter, Depends, Request  # noqa: F401
from pydantic import BaseModel
from src.api import auth
from enum import Enum
import sqlalchemy
from src import database as db
from .utils import inv

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)

class search_sort_options(str, Enum):
    customer_name = "customer_name"
    item_sku = "item_sku"
    line_item_total = "line_item_total"
    timestamp = "timestamp"

class search_sort_order(str, Enum):
    asc = "asc"
    desc = "desc"   

@router.get("/search/", tags=["search"])
def search_orders(
    customer_name: str = "",
    potion_sku: str = "",
    search_page: str = "",
    sort_col: search_sort_options = search_sort_options.timestamp,
    sort_order: search_sort_order = search_sort_order.desc,
):
    """
    Search for cart line items by customer name and/or potion sku.

    Customer name and potion sku filter to orders that contain the 
    string (case insensitive). If the filters aren't provided, no
    filtering occurs on the respective search term.

    Search page is a cursor for pagination. The response to this
    search endpoint will return previous or next if there is a
    previous or next page of results available. The token passed
    in that search response can be passed in the next search request
    as search page to get that page of results.

    Sort col is which column to sort by and sort order is the direction
    of the search. They default to searching by timestamp of the order
    in descending order.

    The response itself contains a previous and next page token (if
    such pages exist) and the results as an array of line items. Each
    line item contains the line item id (must be unique), item sku, 
    customer name, line item total (in gold), and timestamp of the order.
    Your results must be paginated, the max results you can return at any
    time is 5 total line items.
    """

    return {
        "previous": "",
        "next": "",
        "results": [
            {
                "line_item_id": 1,
                "item_sku": "1 oblivion potion",
                "customer_name": "Scaramouche",
                "line_item_total": 50,
                "timestamp": "2021-01-01T00:00:00Z",
            }
        ],
    }


class Customer(BaseModel):
    customer_name: str
    character_class: str
    level: int

@router.post("/visits/{visit_id}")
def post_visits(visit_id: int, customers: list[Customer]):
    """
    Which customers visited the shop today?
    """
    classes = []
    levels = []
    numbers = []
    for person in customers:
        if person.character_class in classes:
            x = classes.index(person.character_class)
            levels[x].append(person.level)
            numbers[x] += 1
        else:
            classes.append(person.character_class)
            levels.append([person.level])
            numbers.append(1)
    print(f"Classes: {classes}")
    print(f"Levels:  {levels}")
    print(f"numbers: {numbers}")
    data = [{"id": visit_id, "class": classes[x], "avg": ((sum(levels[x]))/len(levels[x])), "num": numbers[x] } for x in range(len(classes))]
    print(data)
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("INSERT INTO visits (visit_id, class, lvl_avg, num) VALUES (:id, :class, :avg, :num) "), data)
    print(customers)

    return "OK"


@router.post("/")
def create_cart(new_cart: Customer):
    """ """
    print(Customer)
    with db.engine.begin() as connection:
        id = connection.execute(sqlalchemy.text("INSERT INTO carts_log (customer_name, character_class, level) VALUES (:name, :class, :level) RETURNING id"), {"name": new_cart.customer_name, "class": new_cart.character_class, "level": new_cart.level}).first()[0]
    return {"cart_id": id}


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    print(f"id: {cart_id}, sku {item_sku}, quantity: {cart_item.quantity}")
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("INSERT INTO cart_items (cart_id, item_sku, quantity) VALUES (:id, :sku, :quantity)"), {"id": cart_id, "sku": item_sku, "quantity": cart_item.quantity})
    return "OK"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    print(cart_checkout.payment)
    with db.engine.begin() as connection:
        paid = 0
        quantity = 0
        cart = connection.execute(sqlalchemy.text("SELECT cart_id, item_sku, quantity FROM cart_items WHERE cart_id = :id"), {"id": cart_id})
        
        
        for items in cart:
            
            quantity += items.quantity
            inv.update_potions(items.item_sku, -items.quantity)
            
            paid += inv.get_potions_sku(items.item_sku).price*items.quantity
        inv.update_gold(paid)
        
    return {"total_potions_bought": quantity, "total_gold_paid": paid}
