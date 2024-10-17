from pydantic import BaseModel
import sqlalchemy
from src import database as db

def get_ml():
    with db.engine.begin() as connection:
        ml_log = connection.execute(sqlalchemy.text("SELECT SUM(red_ml) AS red, SUM(green_ml) AS green, SUM(blue_ml) AS blue, SUM(dark_ml) AS dark FROM global_inventory")).first() 
    return[ml_log[0], ml_log[1], ml_log[2], ml_log[3]]

def get_gold():
    with db.engine.begin() as connection:
        gold = connection.execute(sqlalchemy.text("SELECT SUM(gold) FROM global_inventory")).scalar_one()
    return gold

class Potion(BaseModel):
    sku : str
    name : str
    quantity : int
    price : int
    recipe : tuple[int,int,int,int]

def get_potions_sku(sku : str):
    with db.engine.begin() as connection:
        gen = connection.execute(sqlalchemy.text("SELECT * FROM potion_types WHERE potion_sku = :sku"), {"sku": sku}).first()
        quantity = connection.execute(sqlalchemy.text("SELECT SUM(quantity) FROM potion_inventory WHERE sku = :sku"), {"sku": sku}).scalar_one()
        potion = Potion(sku = sku, name = gen.potion_name, quantity = quantity, price = gen.price, recipe = (gen.red_ml, gen.green_ml, gen.blue_ml, gen.dark_ml) )
    return potion

def get_potions_type(type : list[int]):
    with db.engine.begin() as connection:
        potion_log = connection.execute(sqlalchemy.text("SELECT * FROM potion_types WHERE red_ml = :red AND green_ml = :green AND blue_ml = :blue AND dark_ml = :dark"), {"red": type[0], "green": type[1], "blue": type[2], "dark": type[3]}).first()
        potion = Potion(sku = potion_log.potion_sku, name = potion_log.potion_name, quantity = 0, price = potion_log.price, recipe = tuple(type))
    return potion

def get_num_potions_type(sku : str):
    quantity = 0
    with db.engine.begin() as connection:
        quantity = connection.execute(sqlalchemy.text("SELECT SUM(quantity) FROM potion_inventory WHERE sku = :type"), {"type": sku}).scalar_one()
    return quantity

def get_potions_catalog():
    with db.engine.begin() as connection:
        potion_log = connection.execute(sqlalchemy.text("SELECT * FROM potion_types"))
        potions = [Potion(
            sku = i.potion_sku, 
            name = i.potion_name, 
            quantity = get_num_potions_type(i.potion_sku), 
            price = i.price, recipe = (i.red_ml, i.green_ml, i.blue_ml, i.dark_ml)) 
        for i in potion_log]
        return potions

def get_num_potions():
    quantity = 0
    with db.engine.begin() as connection:
        quantity = connection.execute(sqlalchemy.text("SELECT SUM(quantity) FROM potion_inventory")).scalar_one()
    return quantity

def update_ml_full(ml_change : tuple[int,int,int,int]):
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("INSERT INTO global_inventory (red_ml, green_ml, blue_ml, dark_ml) VALUES (:red, :green, :blue, :dark)"), {"red": ml_change[0], "green": ml_change[1], "blue": ml_change[2], "dark": ml_change[3]})
    return "OK"

def update_ml_spec(ml_change : int, type : str):
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("INSERT INTO global_inventory (:type) VALUES (:ml)"), {"type": type, "ml": ml_change})
    return "OK"

def update_gold(gold : int):
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("INSERT INTO global_inventory (gold) VALUES (:gold)"), {"gold": gold})
    return "OK"

def update_potions(sku : str, quantity : int):
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("INSERT INTO potion_inventory (quantity, sku) VALUES (:quantity, :sku)"), {"quantity" : quantity, "sku": sku})
    return "OK"

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int


def update_potions_list(potions: list[PotionInventory]):
    quantities = [p.quantity for p in potions]
    red_mls = [p.potion_type[0] for p in potions]
    green_mls = [p.potion_type[1] for p in potions]
    blue_mls = [p.potion_type[2] for p in potions]
    dark_mls = [p.potion_type[3] for p in potions]
    table_info = [{"quantity": quantities[x], "red_ml" : red_mls[x], "green_ml": green_mls[x], "blue_ml": blue_mls[x], "dark_ml": dark_mls[x]} for x in range(len(potions))]
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("""INSERT INTO potion_inventory (quantity, sku) 
                                           SELECT :quantity, potion_sku
                                           FROM potion_types 
                                           WHERE red_ml = :red_ml AND green_ml = :green_ml AND blue_ml = :blue_ml AND dark_ml = :dark_ml"""),
                                           table_info)
    return "OK"

def get_ml_cap():
    with db.engine.begin() as connection:
        capacity = connection.execute(sqlalchemy.text("SELECT SUM(ml_capacity) FROM capacity")).scalar_one()
        capacity *= 10000
    return capacity
    
def get_potion_cap():
    with db.engine.begin() as connection:
        capacity = connection.execute(sqlalchemy.text("SELECT SUM(potion_capacity) FROM capacity")).scalar_one()
        capacity *= 50
    return capacity

def update_capacity(ml : int, pot : int):
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("INSERT INTO capacity (ml_capacity, potion_capacity) VALUES (:ml, :pot)"), {"ml": ml, "pot": pot})
    return "OK"

def get_date_time():
    with db.engine.begin() as connection:
        date_time = connection.execute(sqlalchemy.text("SELECT day, hour FROM date_time")).first()
    return date_time

def get_next_hour():
    days = ["Edgeday",
            "Bloomday"
            "Aracanaday",
            "Hearthday",
            "Crownday",
            "Blesseday",
            "Soulday"]
    with db.engine.begin() as connection:
        date_time = connection.execute(sqlalchemy.text("SELECT day, hour FROM date_time")).first()
        if (date_time.hour+2) >= 24:
            for x in range(7):
                if date_time.hour == days[x]:
                    date_time.hour = days[x+1]
        date_time.hour = ((date_time.hour + 2) % 24)
    return date_time

def get_top_6(day : str, hour : int):
    with db.engine.begin() as connection:
        Potions = connection.execute(sqlalchemy.text('''
                                                     SELECT sku, weight FROM potion_weights
                                                     JOIN date_time ON date_time.day = potion_weights.day AND date_time.hour = potion_weights.hour
                                                     ORDER BY weight DESC
                                                     LIMIT 6
                                                     ''')).first()

    return