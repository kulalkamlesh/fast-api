from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime ,date

class ItemModel(BaseModel):
    name: str
    email: EmailStr
    item_name: str
    quantity: int
    expiry_date: Optional[date]  # Change date to datetime

class UpdateItemModel(BaseModel):
    name: Optional[str]
    email: Optional[EmailStr]
    item_name: Optional[str]
    quantity: Optional[int]
    expiry_date: Optional[date]

class ClockInModel(BaseModel):
    email: EmailStr
    location: str

class UpdateClockInModel(BaseModel):
    location: Optional[str]
