from pydantic import BaseModel, Field, validator
from typing import Optional

class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Имя товара")
    description: Optional[str] = Field(None, max_length=500, description="Описание")
    price: float = Field(..., gt=0, description="Цена")
    stock_quantity: int = Field(..., ge=0, description="Количество")
    
    @validator('name')
    def validate_name(cls, v):
        if v.strip() == "":
            raise ValueError('Ва-а-а! Имя не может состоять из одних пробелов!')
        return v
    
    @validator('price')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Цена должна быть положительной!')
        return v

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: Optional[float] = Field(None, gt=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    
    @validator('name')
    def validate_name(cls, v):
        if v is not None and v.strip() == "":
            raise ValueError('Ва-а-а! Имя не может быть пустым!')
        return v
    
    @validator('price')
    def validate_price(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Ва-ха-ха! Цена должна быть больше нуля!')
        return v

class Product(ProductBase):
    id: int
    class Config:
        from_attributes = True