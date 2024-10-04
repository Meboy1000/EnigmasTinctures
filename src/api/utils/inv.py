import sqlalchemy
from src import database as db

def get_ml():
    red_ml = 0
    green_ml = 0
    blue_ml = 0
    dark_ml = 0
    with db.engine.begin() as connection:
        ml_log = connection.execute(sqlalchemy.text("SELECT red_ml, green_ml, blue_ml, dark_ml FROM test_global_inventory"))
        for ml in ml_log:
            red_ml += ml.red_ml
            green_ml += ml.green_ml
            blue_ml += ml.blue_ml
            dark_ml += ml.dark_ml
    return[red_ml, green_ml, blue_ml, dark_ml]

def get_gold():
    gold = 0
    with db.engine.begin() as connection:
        gold_log = connection.execute(sqlalchemy.text("SELECT gold FROM test_global_inventory"))
        for g_change in gold_log:
            gold += g_change.gold
    return gold

class Potion():
    sku : str
    name : str
    quantity : int
    price : int
    recipe : tuple[int,int,int,int]

def get_potions_sku(sku : str):
    quantity = 0
    with db.engine.begin() as connection:
        gen = connection.execute(sqlalchemy.text(f"SELECT * FROM potion_types WHERE potion_sku = \'{sku}\'")).first()
        potion_log = connection.execute(sqlalchemy.text(f"SELECT quantity FROM potion_inventory WHERE sku = \'{sku}\'"))
        for entry in potion_log:
            quantity += entry.quantity
        potion = Potion(sku, gen.name, quantity, gen.price, (gen.red_ml, gen.green_ml, gen.blue_ml, gen.dark_ml) )
    return potion

def get_potions_type(type : list[int]):
    with db.engine.begin() as connection:
        potion_log = connection.execute(sqlalchemy.text(f"SELECT FIRST * FROM potion_inventory WHERE red_ml = {type[0]} AND green ml = {type[1]} AND blue_ml = {type[2]} AND dark_ml = {type[3]}"))
        potion = Potion(potion_log.sku, potion_log.name, 0, potion_log.price, tuple(type))
    return potion

def get_num_potions():
    quantity = 0
    with db.engine.begin() as connection:
        potion_log = connection.execute(sqlalchemy.text("SELECT quantity FROM potion_inventory"))
        for entry in potion_log:
            quantity += entry.quantity
    return quantity

def update_ml(ml_change : tuple[int,int,int,int]):
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(f"INSERT INTO test_global_inventory (red_ml, green_ml, blue_ml, dark_ml) VALUES ({ml_change[0]},{ml_change[1]},{ml_change[2]},{ml_change[3]})"))

    return "OK"

def update_gold(gold : int):
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(f"INSERT INTO test_global_inventory (gold) VALUES ({gold})"))
    return "OK"

def update_potions(sku : str, quantity : int):
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(f"INSERT INTO potion_inventory (quantity, sku) VALUES ({quantity}, \'{sku}\')"))
    return "OK"

def get_ml_cap():
    with db.engine.begin() as connection:
        capacity = connection.execute(sqlalchemy.text("SELECT ml_capacity FROM capacity")).first()
        capacity *= 10000
        return capacity