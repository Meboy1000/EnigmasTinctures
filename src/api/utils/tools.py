from pydantic import BaseModel


class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int

def organizeCatalog(wholesale_catalog : list[Barrel]):
    no_barrel = Barrel("Empty", 0, [0,0,0,0], 0, 0)
    red_barrels = [no_barrel,no_barrel,no_barrel,no_barrel]
    green_barrels = [no_barrel,no_barrel,no_barrel,no_barrel]
    blue_barrels = [no_barrel,no_barrel,no_barrel,no_barrel]
    dark_barrels = [no_barrel,no_barrel,no_barrel,no_barrel]
    for barrel in wholesale_catalog:
        ptype = barrel.potion_type
        if ptype == [1,0,0,0]:
            red_barrels = barrelSizer(red_barrels, barrel)
        elif ptype == [0,1,0,0]:
            green_barrels = barrelSizer(green_barrels, barrel)
        elif ptype == [0,0,1,0]:
            blue_barrels = barrelSizer(blue_barrels, barrel)
        elif ptype == [0,0,0,1]:
            dark_barrels = barrelSizer(dark_barrels, barrel)
    catalog = [red_barrels, green_barrels, blue_barrels, dark_barrels]
    return catalog

def barrelSizer(barrel_list : list[Barrel], barrel : Barrel):
    ml = Barrel.ml_per_barrel
    if ml == 200:
        barrel_list[3] = Barrel
    elif ml == 500:
        barrel_list[2] = Barrel
    elif ml == 2500:
        barrel_list[1] = Barrel
    elif ml == 10000:
        barrel_list[0] = Barrel
    return barrel_list