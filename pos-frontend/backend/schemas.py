from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class MenuItemBase(BaseModel):
    name: str
    category: str
    price: float

class MenuItemCreate(MenuItemBase):
    image_url: Optional[str] = None
    pass

class MenuItemOut(MenuItemBase):
    id: int
    name: str
    price: float
    image_url: Optional[str]

    class Config:
        from_attributes = True

class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    image_url: Optional[str] = None
    description: Optional[str] = None

class OrderItemCreate(BaseModel):
    menu_item_id: int
    quantity: int
    discount_person_name: Optional[str] = None
    discount_person_id: Optional[str] = None
    discount_person_type: Optional[str] = None
    manual_discount_type: Optional[str] = None
    manual_discount_value: Optional[float] = 0.0
    notes: Optional[str] = None

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]
    type: Optional[str] = "dine-in"
    notes: Optional[str] = None
    paid_amount: Optional[float] = 0.0
    discount: Optional[float] = 0.0
    cashier: Optional[str] = None 

class OrderItemOut(BaseModel):
    id: int
    order_id: int
    quantity: int
    menu_item: MenuItemOut
    discount_person_name: Optional[str]
    discount_person_id: Optional[str]
    discount_person_type: Optional[str]
    manual_discount_type: Optional[str]
    manual_discount_value: Optional[float]
    notes: Optional[str] = None

    class Config:
        from_attributes = True

class OrderOut(BaseModel):
    id: int
    created_at: datetime
    total: float
    discount: Optional[float] = 0.0
    paid: Optional[float] = 0.0
    is_paid: bool
    notes: Optional[str]
    items: List[OrderItemOut]
    cancel_reason: Optional[str] = None
    type: Optional[str]
    status: Optional[str]
    receipt_number: Optional[str]
    cashier: Optional[str] = None 

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "cashier"  

class UserOut(BaseModel):
    id: int
    username: str
    role: str

    class Config:
        from_attributes = True    
        
class SalesSummary(BaseModel):
    total_paid: float
    total_unpaid: float
    orders_paid: int
    orders_unpaid: int
    total_discount: float
    dine_in_count: int
    dine_in_sales: float
    take_out_count: int
    take_out_sales: float
    void_orders: int

        
class DiscountUpdate(BaseModel):
    discount: float = Field(..., ge=0)
    
class UpdateQuantity(BaseModel):
    quantity: int   
    
class PayData(BaseModel):
    paid: float    
    change: Optional[float] = 0

class CancelOrderRequest(BaseModel):
    cancel_reason: Optional[str] = None            

class OrderItemUpdate(BaseModel):
    menu_item_id: int
    quantity: int

class OrderUpdate(BaseModel):
    type: str
    notes: Optional[str]
    items: List[OrderItemUpdate]
    status: Optional[str]

# --- Supervisor & Cashier PIN Management --- #

class SupervisorUpdate(BaseModel):
    pin: str


class CashierCreate(BaseModel):
    name: str
    pin: str


class CashierOut(BaseModel):
    id: int
    name: str
    pin: str

    class Config:
        from_attributes = True


class CashierUpdate(BaseModel):
    name: Optional[str] = None
    pin: Optional[str] = None
    

class SettingUpdate(BaseModel):
    value: str    