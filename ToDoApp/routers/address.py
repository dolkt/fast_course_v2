import sys
sys.path.append("...")

from fastapi import Depends, APIRouter
from typing import Union
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel
from routers.auth import get_current_user, get_user_exception
import models


router = APIRouter(
    prefix="/address",
    tags=["address"],
    responses={404: {"description": "Not found"}}
)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


class Address(BaseModel):
    address1: str
    address2: Union[str, None] = None
    apt_num: Union[str, None] = None
    city: str
    state: str
    country: str
    postalcode: str


@router.post("/")
async def create_address(address: Address, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):

    if user is None:
        raise get_user_exception()

    address_model = models.Address()

    address_model.address1 = address.address1
    address_model.address2 = address.address2
    address_model.city = address.city
    address_model.state = address.state
    address_model.country = address.country
    address_model.postalcode = address.postalcode
    address_model.apt_num = address.apt_num

    db.add(address_model)
    db.flush()

    user_model = db.query(models.Users).filter(models.Users.user_id == user.get("user_id")).first()

    user_model.address_id = address_model.id

    db.add(user_model)
    db.commit()

    return {"message": f"address updated for {user.get('user_id')}"}    



    