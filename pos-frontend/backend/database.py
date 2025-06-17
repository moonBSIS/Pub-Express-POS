from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from passlib.context import CryptContext
from datetime import datetime
from pydantic import BaseModel
from typing import Optional
import os, sys

# Database URL (SQLite)
if getattr(sys, 'frozen', False):  # Running as exe
    BASE_DIR = os.path.expanduser(os.path.join('~', 'AppData', 'Local', 'PubExpressPOS'))
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

os.makedirs(BASE_DIR, exist_ok=True)
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'pub_express.db')}"

# Create engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Define Base class for ORM models
Base = declarative_base()

# Create database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Hashing settings
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    category = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    image_url = Column(String, nullable=True)

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    total = Column(Float, default=0.0)
    discount = Column(Float, default=0.0)
    paid = Column(Float, default=0.0)
    is_paid = Column(Boolean, default=False)
    type = Column(String, default="dine-in")
    notes = Column(String, nullable=True)
    cancel_reason = Column(String, nullable=True)
    status = Column(String, default="new")
    receipt_number = Column(String, nullable=True, unique=True)
    cashier = Column(String, nullable=True)

    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"))
    quantity = Column(Integer, default=1)

    discount_person_name = Column(String, nullable=True)
    discount_person_id = Column(String, nullable=True)
    discount_person_type = Column(String, nullable=True)
    
    manual_discount_type = Column(String, nullable=True)
    manual_discount_value = Column(Float, default=0.0)
    notes = Column(String, nullable=True)


    order = relationship("Order", back_populates="items")
    menu_item = relationship("MenuItem") 

class Supervisor(Base):
    __tablename__ = "supervisors"

    id = Column(Integer, primary_key=True, index=True)
    pin = Column(String, nullable=False)


class Cashier(Base):
    __tablename__ = "cashiers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    pin = Column(String, nullable=False)

class Setting(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, nullable=False)
    value = Column(String, nullable=True)

Base.metadata.create_all(bind=engine)
