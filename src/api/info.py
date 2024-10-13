from fastapi import APIRouter, Depends, Request  # noqa: F401
from pydantic import BaseModel
from src.api import auth
from src import database as db
import sqlalchemy
router = APIRouter(
    prefix="/info",
    tags=["info"],
    dependencies=[Depends(auth.get_api_key)],
)

class Timestamp(BaseModel):
    day: str
    hour: int

@router.post("/current_time")
def post_time(timestamp: Timestamp):
    print(f"Today is {timestamp.day}\nIt is hour {timestamp.hour}")
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("UPDATE date_time SET day = :day, hour = :hour "), {"hour": timestamp.hour, "day": timestamp.day})
    return "OK"

