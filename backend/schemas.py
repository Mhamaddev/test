from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    pass

class Product(ProductBase):
    id: int

    class Config:
        orm_mode = True

class TransactionItemBase(BaseModel):
    product_id: int
    quantity: int

class TransactionItemCreate(TransactionItemBase):
    pass

class TransactionItem(TransactionItemBase):
    id: int
    price: float

    class Config:
        orm_mode = True

class TransactionBase(BaseModel):
    pass

class TransactionCreate(TransactionBase):
    items: List[TransactionItemCreate]

class Transaction(TransactionBase):
    id: int
    user_id: int
    created_at: datetime
    total_price: float
    items: List[TransactionItem] = []

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None 