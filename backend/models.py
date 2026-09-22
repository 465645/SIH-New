from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from database import Base
import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class PackagingReport(Base):
    __tablename__ = "packaging_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Links report to the logged-in user
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # User Inputs
    product_name = Column(String, index=True)
    fssai_category = Column(String)
    shelf_life_days = Column(Integer)
    is_liquid = Column(Boolean)
    
    # ML Model Outputs
    optimal_material = Column(String)
    barrier_requirement = Column(String)
    map_gas = Column(String)
    estimated_cost_per_unit = Column(Float)
    epr_green_score = Column(Integer)