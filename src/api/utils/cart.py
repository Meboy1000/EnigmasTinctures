import sqlalchemy
from src import database as db

def get_cart():
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text())
    return