from pydantic import BaseModel


class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int
# organizes barrel catalog by ml type and then by size descending.
def organizeCatalog(wholesale_catalog : list[Barrel]):
    no_barrel = Barrel(sku = "Empty",
                        ml_per_barrel= 0,
                        potion_type = [0,0,0,0],
                        price = 0,
                        quantity = 0)
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

# organizes list of barrels by amount of ml, not flexible, only easily usable by above method
def barrelSizer(barrel_list : list[Barrel], barrel : Barrel):
    ml = barrel.ml_per_barrel
    if ml == 200:
        barrel_list[3] = barrel
    elif ml == 500:
        barrel_list[2] = barrel
    elif ml == 2500:
        barrel_list[1] = barrel
    elif ml == 10000:
        barrel_list[0] = barrel
    return barrel_list