from sqlalchemy import Column, Integer, String, Date, Float, DateTime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, index=True)
    phone = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    # الحقول الجديدة المضافة لاستعادة كلمة المرور
    reset_otp = Column(String, nullable=True)
    otp_expiry = Column(DateTime, nullable=True)
    

# يمثل شيت "الموظفين"
class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    iqama_expiry = Column(Date)
    passport_expiry = Column(Date)
    health_insurance_expiry = Column(Date)

# يمثل شيت "السيارات"
class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    plate_number = Column(String, index=True)
    insurance_expiry = Column(Date)
    registration_expiry = Column(Date) # استمارة السيارة