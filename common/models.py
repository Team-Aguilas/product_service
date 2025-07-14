from bson import ObjectId
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List
from pydantic_core import core_schema

class PyObjectId(ObjectId):
    @classmethod
    def _validate(cls, v, _validation_info=None):
        if isinstance(v, ObjectId): return v
        if ObjectId.is_valid(v): return ObjectId(v)
        raise ValueError(f"'{v}' no es un ObjectId válido")
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        return core_schema.json_or_python_schema(
            python_schema=core_schema.with_info_plain_validator_function(cls._validate),
            json_schema=core_schema.str_schema(pattern=r'^[0-9a-fA-F]{24}$'),
            serialization=core_schema.to_string_ser_schema()
        )
    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema_obj, handler):
        return {"type": "string", "pattern": r"^[0-9a-fA-F]{24}$", "example": "507f1f77bcf86cd799439011"}

class DBModelMixin(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True, json_encoders={ObjectId: str, PyObjectId: str})

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=100)
class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None
class UserInDB(DBModelMixin, UserBase):
    hashed_password: str
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
class UserRead(UserBase):
    id: PyObjectId = Field(alias="_id")
    is_active: bool
    is_superuser: bool
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True, json_encoders={ObjectId: str})

class ProductBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    whatsapp_number: str = Field(..., examples=["573001234567"])
    description: Optional[str] = Field(None, max_length=500)
    price: float = Field(..., gt=0)
    currency: str = Field("COP")
    stock: int = Field(..., ge=0)
    category: str
    image_url: Optional[str] = None
    tags: Optional[List[str]] = None
    owner_id: Optional[PyObjectId] = None
    average_rating: Optional[float] = Field(default=0.0, ge=0, le=5)
    total_ratings: Optional[int] = Field(default=0, ge=0)
    
class ProductCreate(ProductBase):
    owner_id: Optional[PyObjectId] = Field(None, exclude=True)

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    whatsapp_number: Optional[str] = None
    description: Optional[str] = Field(None, max_length=500)
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    category: Optional[str] = None
    image_url: Optional[str] = None
    tags: Optional[List[str]] = None

class ProductInDB(DBModelMixin, ProductBase):
    owner_id: PyObjectId

class ProductRead(ProductBase):
    id: PyObjectId = Field(alias="_id")
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True, json_encoders={ObjectId: str})

class Token(BaseModel):
    access_token: str
    token_type: str
class TokenData(BaseModel):
    user_id: Optional[str] = None

# Modelos para el sistema de calificaciones
class RatingBase(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=500)

class RatingInput(RatingBase):
    """Modelo para crear ratings desde el endpoint (sin product_id porque viene en la URL)"""
    pass

class RatingCreate(RatingBase):
    product_id: PyObjectId
    user_id: Optional[PyObjectId] = Field(None, exclude=True)

class RatingInDB(DBModelMixin, RatingBase):
    product_id: PyObjectId
    user_id: PyObjectId

class RatingRead(RatingBase):
    id: PyObjectId = Field(alias="_id")
    product_id: PyObjectId
    user_id: PyObjectId
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True, json_encoders={ObjectId: str})