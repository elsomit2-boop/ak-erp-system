from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import create_engine, Column, Integer, String, Date, Float
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from pydantic import BaseModel, root_validator
from datetime import date
import json
import hashlib
from typing import Optional, List, Dict, Any

# ==========================================
# 1. إعدادات قاعدة البيانات (Supabase PostgreSQL Cloud)
# ==========================================

# 💡 ضع رابط Supabase المشفر الخاص بك هنا
# تذكر استبدال [YOUR-PASSWORD] بكلمة المرور الحقيقية التي أنشأتها (بدون الأقواس המربعة [])
SQLALCHEMY_DATABASE_URL = "postgresql://postgres.ytfkmuvlbuzbhjthurzv:Aa01093179299Aa@aws-0-ap-northeast-1.pooler.supabase.com:6543/postgres"

engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

# دوال التشفير الأساسية
def get_password_hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return get_password_hash(plain_password) == hashed_password

# ==========================================
# 2. نماذج قاعدة البيانات (Models) السحابية
# ==========================================
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    phone = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True); owner_id = Column(Integer, index=True)
    name = Column(String); iqama_number = Column(String); iqama_expiry = Column(Date, nullable=True)
    health_insurance_expiry = Column(Date, nullable=True); sponsorship = Column(String); passport_expiry = Column(Date, nullable=True)

class Vehicle(Base):
    __tablename__ = "vehicles"
    id = Column(Integer, primary_key=True, index=True); owner_id = Column(Integer, index=True)
    car_name = Column(String); plate_number = Column(String); registration_number = Column(String)
    registration_expiry = Column(Date, nullable=True); insurance_expiry = Column(Date, nullable=True)

class Visa(Base):
    __tablename__ = "visas"
    id = Column(Integer, primary_key=True, index=True); owner_id = Column(Integer, index=True)
    employee_name = Column(String); visa_number = Column(String); travel_date = Column(Date, nullable=True)
    visa_duration_months = Column(String); visa_duration_days = Column(String); extension_count = Column(Integer, default=0)
    expiry_date = Column(Date, nullable=True); notes = Column(String)

class Rent(Base):
    __tablename__ = "rents"
    id = Column(Integer, primary_key=True, index=True); owner_id = Column(Integer, index=True)
    tenant_name = Column(String); apartment_number = Column(String); contract_number = Column(String)
    contract_start_date = Column(Date, nullable=True); contract_duration = Column(String); contract_expiry = Column(Date, nullable=True)
    next_payment_date = Column(Date, nullable=True); payment_amount = Column(String); payment_period_months = Column(String); annual_rent = Column(String)

class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True, index=True); owner_id = Column(Integer, index=True)
    service_name = Column(String); subscription_number = Column(String); subscription_expiry = Column(Date, nullable=True); notes = Column(String)

class Installment(Base):
    __tablename__ = "installments"
    id = Column(Integer, primary_key=True, index=True); owner_id = Column(Integer, index=True)
    client_name = Column(String); title = Column(String); total_amount = Column(Float); advance_payment = Column(Float)
    installments_count = Column(Integer); period_months = Column(Integer); first_installment_date = Column(Date, nullable=True)
    payments_data = Column(String); notes = Column(String)

class Setting(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True, index=True); owner_id = Column(Integer, index=True)
    section = Column(String); warning_days = Column(Integer, default=30); danger_days = Column(Integer, default=0)

class CustomPage(Base):
    __tablename__ = "custom_pages"
    id = Column(Integer, primary_key=True, index=True); owner_id = Column(Integer, index=True)
    title = Column(String); columns_data = Column(String)

class CustomRecord(Base):
    __tablename__ = "custom_records"
    id = Column(Integer, primary_key=True, index=True); owner_id = Column(Integer, index=True); page_id = Column(Integer, index=True); record_data = Column(String)

class ExtraPage(Base):
    __tablename__ = "extra_pages"
    id = Column(Integer, primary_key=True, index=True); owner_id = Column(Integer, index=True)
    title = Column(String); columns_data = Column(String)

class ExtraRecord(Base):
    __tablename__ = "extra_records"
    id = Column(Integer, primary_key=True, index=True); owner_id = Column(Integer, index=True); page_id = Column(Integer, index=True); record_data = Column(String)

class ManagerPage(Base):
    __tablename__ = "manager_pages"
    id = Column(Integer, primary_key=True, index=True); owner_id = Column(Integer, index=True)
    title = Column(String); columns_data = Column(String)

class ManagerRecord(Base):
    __tablename__ = "manager_records"
    id = Column(Integer, primary_key=True, index=True); owner_id = Column(Integer, index=True); page_id = Column(Integer, index=True); record_data = Column(String)

class PayrollRecord(Base):
    __tablename__ = "payroll_records"
    id = Column(Integer, primary_key=True, index=True); owner_id = Column(Integer, index=True)
    year = Column(Integer, index=True); month = Column(String, index=True); record_data = Column(String)

class EmployeeLoanRecord(Base):
    __tablename__ = "employee_loans"
    id = Column(Integer, primary_key=True, index=True); owner_id = Column(Integer, index=True)
    employee_name = Column(String, index=True); year = Column(Integer, index=True); record_data = Column(String)

class SupportSalaryRecord(Base):
    __tablename__ = "support_salaries"
    id = Column(Integer, primary_key=True, index=True); owner_id = Column(Integer, index=True)
    year = Column(Integer, index=True); record_data = Column(String)

class AnnualReportRecord(Base):
    __tablename__ = "annual_reports"
    id = Column(Integer, primary_key=True, index=True); owner_id = Column(Integer, index=True)
    employee_name = Column(String, index=True); year = Column(Integer, index=True); record_data = Column(String)

Base.metadata.create_all(bind=engine)
app = FastAPI(title="A.K ERP System - API")

# ==========================================
# 3. نظام المصادقة Pydantic
# ==========================================
class UserCreate(BaseModel):
    full_name: str; phone: str; email: str; password: str

class UserLogin(BaseModel):
    email: str; password: str

@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter((User.email == user.email) | (User.phone == user.phone)).first():
        raise HTTPException(status_code=400, detail="البريد الإلكتروني أو رقم الجوال مسجل مسبقاً في النظام")
    
    hashed_pwd = get_password_hash(user.password)
    new_user = User(full_name=user.full_name, phone=user.phone, email=user.email, hashed_password=hashed_pwd)
    
    db.add(new_user); db.commit(); db.refresh(new_user)
    
    sections = ["الموظفين", "السيارات", "التأشيرات", "عقود الإيجار", "الاشتراكات العامة", "الأقساط"]
    for sec in sections: db.add(Setting(section=sec, warning_days=30, danger_days=0, owner_id=new_user.id))
    db.commit()
    return {"id": new_user.id, "name": new_user.full_name}

@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="بيانات الدخول (البريد أو كلمة المرور) غير صحيحة")
    return {"id": db_user.id, "name": db_user.full_name}

def replace_empty_with_none(values):
    for key, val in values.items():
        if isinstance(val, str) and not val.strip(): values[key] = "لا يوجد"
    return values

class EmployeeBase(BaseModel): 
    owner_id: int; name: Optional[str] = "لا يوجد"; iqama_number: Optional[str] = "لا يوجد"; iqama_expiry: Optional[date] = None; health_insurance_expiry: Optional[date] = None; sponsorship: Optional[str] = "لا يوجد"; passport_expiry: Optional[date] = None
    @root_validator(pre=True)
    def check_empty(cls, values): return replace_empty_with_none(values)

class VehicleBase(BaseModel): 
    owner_id: int; car_name: Optional[str] = "لا يوجد"; plate_number: Optional[str] = "لا يوجد"; registration_number: Optional[str] = "لا يوجد"; registration_expiry: Optional[date] = None; insurance_expiry: Optional[date] = None
    @root_validator(pre=True)
    def check_empty(cls, values): return replace_empty_with_none(values)

class VisaBase(BaseModel): 
    owner_id: int; employee_name: Optional[str] = "لا يوجد"; visa_number: Optional[str] = "لا يوجد"; travel_date: Optional[date] = None; visa_duration_months: Optional[str] = "0"; visa_duration_days: Optional[str] = "0"; extension_count: Optional[int] = 0; expiry_date: Optional[date] = None; notes: Optional[str] = "لا يوجد"
    @root_validator(pre=True)
    def check_empty(cls, values): return replace_empty_with_none(values)

class RentBase(BaseModel): 
    owner_id: int; tenant_name: Optional[str] = "لا يوجد"; apartment_number: Optional[str] = "لا يوجد"; contract_number: Optional[str] = "لا يوجد"; contract_start_date: Optional[date] = None; contract_duration: Optional[str] = "لا يوجد"; contract_expiry: Optional[date] = None; next_payment_date: Optional[date] = None; payment_amount: Optional[str] = "لا يوجد"; payment_period_months: Optional[str] = "لا يوجد"; annual_rent: Optional[str] = "لا يوجد"
    @root_validator(pre=True)
    def check_empty(cls, values): return replace_empty_with_none(values)

class SubscriptionBase(BaseModel): 
    owner_id: int; service_name: Optional[str] = "لا يوجد"; subscription_number: Optional[str] = "لا يوجد"; subscription_expiry: Optional[date] = None; notes: Optional[str] = "لا يوجد"
    @root_validator(pre=True)
    def check_empty(cls, values): return replace_empty_with_none(values)

class InstallmentBase(BaseModel):
    owner_id: int; client_name: Optional[str] = "لا يوجد"; title: Optional[str] = "لا يوجد"; total_amount: Optional[float] = 0.0; advance_payment: Optional[float] = 0.0; installments_count: Optional[int] = 1; period_months: Optional[int] = 1; first_installment_date: Optional[date] = None; payments_data: Optional[str] = "[]"; notes: Optional[str] = "لا يوجد"
    @root_validator(pre=True)
    def check_empty(cls, values): return replace_empty_with_none(values)

class CustomPageBase(BaseModel): owner_id: int; title: str; columns_data: str
class ExtraPageBase(BaseModel): owner_id: int; title: str; columns_data: str
class ManagerPageBase(BaseModel): owner_id: int; title: str; columns_data: str
class SyncRecordsRequest(BaseModel): owner_id: int; records: List[Dict[str, Any]]
class SettingUpdateBase(BaseModel): owner_id: int; warning_days: int; danger_days: int

class PayrollSyncRequest(BaseModel): owner_id: int; records: List[Dict[str, Any]]
class LoanSyncRequest(BaseModel): owner_id: int; records: List[Dict[str, Any]]
class SupportSyncRequest(BaseModel): owner_id: int; records: List[Dict[str, Any]]
class AnnualSyncRequest(BaseModel): owner_id: int; records: List[Dict[str, Any]]

# ==========================================
# 4. مسارات الأقسام الأساسية
# ==========================================
def crud_router(app, endpoint, db_model, pydantic_model):
    @app.post(f"/{endpoint}/")
    def create_item(item: pydantic_model, db: Session = Depends(get_db)):
        db.add(db_model(**item.dict(exclude_unset=True))); db.commit(); return {"msg": "ok"}
    @app.get(f"/{endpoint}/{{user_id}}")
    def read_items(user_id: int, db: Session = Depends(get_db)): 
        return db.query(db_model).filter(db_model.owner_id == user_id).all()
    @app.put(f"/{endpoint}/{{item_id}}")
    def update_item(item_id: int, item: pydantic_model, db: Session = Depends(get_db)):
        db_item = db.query(db_model).filter(db_model.id == item_id, db_model.owner_id == item.owner_id).first()
        if not db_item: return {"error": "not found"}
        for k, v in item.dict(exclude_unset=True, exclude={"owner_id"}).items(): setattr(db_item, k, v)
        db.commit(); return {"msg": "ok"}
    @app.delete(f"/{endpoint}/{{item_id}}/{{user_id}}")
    def delete_item(item_id: int, user_id: int, db: Session = Depends(get_db)):
        db_item = db.query(db_model).filter(db_model.id == item_id, db_model.owner_id == user_id).first()
        if db_item: db.delete(db_item); db.commit()
        return {"msg": "ok"}

crud_router(app, "employees", Employee, EmployeeBase)
crud_router(app, "vehicles", Vehicle, VehicleBase)
crud_router(app, "visas", Visa, VisaBase)
crud_router(app, "rents", Rent, RentBase)
crud_router(app, "subscriptions", Subscription, SubscriptionBase)
crud_router(app, "installments", Installment, InstallmentBase)
crud_router(app, "custom_pages", CustomPage, CustomPageBase)
crud_router(app, "extra_pages", ExtraPage, ExtraPageBase)
crud_router(app, "manager_pages", ManagerPage, ManagerPageBase)

@app.get("/custom_records/{user_id}")
def read_custom_recs(user_id: int, db: Session = Depends(get_db)): return db.query(CustomRecord).filter(CustomRecord.owner_id == user_id).all()
@app.get("/extra_records/{user_id}")
def read_extra_recs(user_id: int, db: Session = Depends(get_db)): return db.query(ExtraRecord).filter(ExtraRecord.owner_id == user_id).all()
@app.get("/manager_records/{user_id}")
def read_mgr_recs(user_id: int, db: Session = Depends(get_db)): return db.query(ManagerRecord).filter(ManagerRecord.owner_id == user_id).all()

@app.post("/custom_pages/{page_id}/sync")
def sync_custom_records(page_id: int, payload: SyncRecordsRequest, db: Session = Depends(get_db)):
    db.query(CustomRecord).filter(CustomRecord.page_id == page_id, CustomRecord.owner_id == payload.owner_id).delete()
    for rec in payload.records: db.add(CustomRecord(page_id=page_id, owner_id=payload.owner_id, record_data=json.dumps(rec)))
    db.commit(); return {"msg": "ok"}

@app.post("/extra_pages/{page_id}/sync")
def sync_extra_records(page_id: int, payload: SyncRecordsRequest, db: Session = Depends(get_db)):
    db.query(ExtraRecord).filter(ExtraRecord.page_id == page_id, ExtraRecord.owner_id == payload.owner_id).delete()
    for rec in payload.records: db.add(ExtraRecord(page_id=page_id, owner_id=payload.owner_id, record_data=json.dumps(rec)))
    db.commit(); return {"msg": "ok"}

@app.post("/manager_pages/{page_id}/sync")
def sync_manager_records(page_id: int, payload: SyncRecordsRequest, db: Session = Depends(get_db)):
    db.query(ManagerRecord).filter(ManagerRecord.page_id == page_id, ManagerRecord.owner_id == payload.owner_id).delete()
    for rec in payload.records: db.add(ManagerRecord(page_id=page_id, owner_id=payload.owner_id, record_data=json.dumps(rec)))
    db.commit(); return {"msg": "ok"}

@app.get("/payroll/{year}/{month}/{user_id}")
def get_payroll(year: int, month: str, user_id: int, db: Session = Depends(get_db)):
    record = db.query(PayrollRecord).filter(PayrollRecord.year == year, PayrollRecord.month == month, PayrollRecord.owner_id == user_id).first()
    return json.loads(record.record_data) if record else []

@app.post("/payroll/{year}/{month}/sync")
def sync_payroll(year: int, month: str, payload: PayrollSyncRequest, db: Session = Depends(get_db)):
    db.query(PayrollRecord).filter(PayrollRecord.year == year, PayrollRecord.month == month, PayrollRecord.owner_id == payload.owner_id).delete()
    db.add(PayrollRecord(year=year, month=month, owner_id=payload.owner_id, record_data=json.dumps(payload.records)))
    db.commit(); return {"msg": "ok"}

@app.get("/loans/{employee}/{year}/{user_id}")
def get_loans(employee: str, year: int, user_id: int, db: Session = Depends(get_db)):
    record = db.query(EmployeeLoanRecord).filter(EmployeeLoanRecord.employee_name == employee, EmployeeLoanRecord.year == year, EmployeeLoanRecord.owner_id == user_id).first()
    return json.loads(record.record_data) if record else []

@app.post("/loans/{employee}/{year}/sync")
def sync_loans(employee: str, year: int, payload: LoanSyncRequest, db: Session = Depends(get_db)):
    db.query(EmployeeLoanRecord).filter(EmployeeLoanRecord.employee_name == employee, EmployeeLoanRecord.year == year, EmployeeLoanRecord.owner_id == payload.owner_id).delete()
    db.add(EmployeeLoanRecord(employee_name=employee, year=year, owner_id=payload.owner_id, record_data=json.dumps(payload.records)))
    db.commit(); return {"msg": "ok"}

@app.get("/support_salary/{year}/{user_id}")
def get_support_salary(year: int, user_id: int, db: Session = Depends(get_db)):
    record = db.query(SupportSalaryRecord).filter(SupportSalaryRecord.year == year, SupportSalaryRecord.owner_id == user_id).first()
    return json.loads(record.record_data) if record else []

@app.post("/support_salary/{year}/sync")
def sync_support_salary(year: int, payload: SupportSyncRequest, db: Session = Depends(get_db)):
    db.query(SupportSalaryRecord).filter(SupportSalaryRecord.year == year, SupportSalaryRecord.owner_id == payload.owner_id).delete()
    db.add(SupportSalaryRecord(year=year, owner_id=payload.owner_id, record_data=json.dumps(payload.records)))
    db.commit(); return {"msg": "ok"}

@app.get("/annual_report/{employee}/{year}/{user_id}")
def get_annual_report(employee: str, year: int, user_id: int, db: Session = Depends(get_db)):
    record = db.query(AnnualReportRecord).filter(AnnualReportRecord.employee_name == employee, AnnualReportRecord.year == year, AnnualReportRecord.owner_id == user_id).first()
    return json.loads(record.record_data) if record else []

@app.post("/annual_report/{employee}/{year}/sync")
def sync_annual_report(employee: str, year: int, payload: AnnualSyncRequest, db: Session = Depends(get_db)):
    db.query(AnnualReportRecord).filter(AnnualReportRecord.employee_name == employee, AnnualReportRecord.year == year, AnnualReportRecord.owner_id == payload.owner_id).delete()
    db.add(AnnualReportRecord(employee_name=employee, year=year, owner_id=payload.owner_id, record_data=json.dumps(payload.records)))
    db.commit(); return {"msg": "ok"}

@app.get("/settings/{user_id}")
def get_settings(user_id: int, db: Session = Depends(get_db)):
    settings = db.query(Setting).filter(Setting.owner_id == user_id).all()
    return {s.section: {"warning_days": s.warning_days, "danger_days": s.danger_days} for s in settings}

@app.put("/settings/{section_name}")
def update_setting(section_name: str, setting: SettingUpdateBase, db: Session = Depends(get_db)):
    db_setting = db.query(Setting).filter(Setting.section == section_name, Setting.owner_id == setting.owner_id).first()
    if db_setting:
        db_setting.warning_days = setting.warning_days; db_setting.danger_days = setting.danger_days; db.commit(); return {"msg": "ok"}
    return {"error": "not found"}

# ==========================================
# 5. التقرير اليومي والنسخ الاحتياطي
# ==========================================
@app.get("/api/backup/{user_id}")
def generate_backup(user_id: int, db: Session = Depends(get_db)):
    backup = {
        "employees": [e.__dict__ for e in db.query(Employee).filter(Employee.owner_id == user_id).all()],
        "vehicles": [v.__dict__ for v in db.query(Vehicle).filter(Vehicle.owner_id == user_id).all()],
        "visas": [v.__dict__ for v in db.query(Visa).filter(Visa.owner_id == user_id).all()],
        "rents": [r.__dict__ for r in db.query(Rent).filter(Rent.owner_id == user_id).all()],
        "installments": [i.__dict__ for i in db.query(Installment).filter(Installment.owner_id == user_id).all()],
    }
    for k in backup:
        for item in backup[k]:
            item.pop('_sa_instance_state', None)
            for sub_k, sub_v in item.items():
                if isinstance(sub_v, date): item[sub_k] = sub_v.isoformat()
    return backup

@app.get("/api/daily-report/{user_id}")
def get_daily_alerts(user_id: int, db: Session = Depends(get_db)):
    today = date.today(); alerts = []
    settings = {s.section: {"warn": s.warning_days, "danger": s.danger_days} for s in db.query(Setting).filter(Setting.owner_id == user_id).all()}
    def check_alerts(query, sec_name, sec_db_name, name_attr, date_attr):
        items = db.query(query).filter(query.owner_id == user_id).all()
        warn_days = settings.get(sec_db_name, {}).get("warn", 30)
        danger_days = settings.get(sec_db_name, {}).get("danger", 0)
        for item in items:
            exp_date = getattr(item, date_attr)
            if exp_date:
                days = (exp_date - today).days
                if days <= warn_days:
                    display_name = getattr(item, name_attr)
                    if sec_name == "السيارات":
                        car_n = getattr(item, "car_name")
                        if car_n and car_n != "لا يوجد": display_name = f"{car_n} - {display_name}"
                    alerts.append({"القسم": sec_name, "البيان": display_name, "تاريخ_الانتهاء": exp_date, "الايام_المتبقية": days, "الحالة": "حرج" if days <= danger_days else "تحذير"})
    
    check_alerts(Employee, "الإقامات", "الموظفين", "name", "iqama_expiry")
    check_alerts(Vehicle, "السيارات", "السيارات", "plate_number", "registration_expiry")
    check_alerts(Visa, "التأشيرات", "التأشيرات", "employee_name", "expiry_date")
    check_alerts(Rent, "الإيجارات", "عقود الإيجار", "tenant_name", "contract_expiry")
    check_alerts(Subscription, "الاشتراكات", "الاشتراكات العامة", "service_name", "subscription_expiry")
    
    inst_items = db.query(Installment).filter(Installment.owner_id == user_id).all()
    inst_warn = settings.get("الأقساط", {}).get("warn", 30); inst_danger = settings.get("الأقساط", {}).get("danger", 0)
    for plan in inst_items:
        try: payments = json.loads(plan.payments_data)
        except: payments = []
        for p in payments:
            amt_due = round(float(p.get("amount_due", 0)), 2); amt_paid = round(float(p.get("paid_amount", 0)), 2)
            if amt_paid < amt_due and p.get("due_date"):
                due_date = date.fromisoformat(p.get("due_date")); days = (due_date - today).days
                if days <= inst_warn:
                    alerts.append({"القسم": "الأقساط", "البيان": f"{plan.client_name} - قسط رقم {p.get('installment_number')} ({round(amt_due - amt_paid, 2)} ريال)", "تاريخ_الانتهاء": due_date, "الايام_المتبقية": days, "الحالة": "حرج" if days <= inst_danger else "تحذير"})
                break 
    return {"إجمالي التنبيهات": len(alerts), "التفاصيل": alerts}