import streamlit as st
from streamlit_option_menu import option_menu
import requests
import pandas as pd
import io
import time
from datetime import date
import calendar
import json
import numpy as np
import datetime

# استيراد مدير الكوكيز الحديث
try:
    import extra_streamlit_components as stx
except ImportError:
    st.error("الرجاء تثبيت المكتبة عبر: pip install extra-streamlit-components")
    st.stop()

try:
    from hijri_converter import Gregorian, Hijri
    HAS_HIJRI = True
except ImportError:
    HAS_HIJRI = False

# ==========================================
# 1. الإعدادات والـ CSS
# ==========================================
st.set_page_config(page_title="A.K ERP System", page_icon="💠", layout="wide", initial_sidebar_state="expanded")
API_URL = "https://ak-erp-system.onrender.com"

# تهيئة مدير الكوكيز بالطريقة المباشرة
cookie_manager = stx.CookieManager(key="ak_erp_cookie_manager")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&family=Tajawal:wght@400;500;700;900&display=swap');
    
    /* 1. الإعدادات الأساسية والاتجاه (RTL) */
    .stApp, html, body { 
        direction: rtl !important; 
        text-align: right !important; 
        font-family: 'Cairo', sans-serif !important; 
        background-color: #F4F7FE !important; 
    }
    
    /* 2. عكس ترتيب الأعمدة لتتوافق مع العربية */
    div[data-testid="stHorizontalBlock"] { flex-direction: row-reverse !important; }
    
    /* 3. توحيد اتجاه النصوص والألوان */
    .stMarkdown, h1, h2, h3, h4, h5, h6, label, input, textarea, select { 
        text-align: right !important; 
        direction: rtl !important; 
        color: #1B2559 !important; 
    }

    /* 4. إخفاء العناصر غير المرغوب فيها */
    header[data-testid="stHeader"] { background-color: transparent !important; direction: ltr !important; }
    .stDeployButton {display: none !important;}
    #MainMenu, footer {display:none !important;}

    /* 5. تصميم القائمة الجانبية المستقر */
    section[data-testid="stSidebar"] { 
        background: linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%) !important; 
        border-right: none !important;
        border-left: none !important; 
    }
    
    section[data-testid="stSidebar"][aria-expanded="true"] {
        border-left: 1px solid #E2E8F0 !important;
    }
    
    /* 💡 إخفاء عنوان قائمة Option Menu 💡 */
    .nav-title {
       display: none !important;
    }

    /* 💡 منع النصوص من الالتفاف عامودياً أثناء إغلاق القائمة لتجنب التشوه 💡 */
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2 {
        white-space: nowrap !important;
    }
    
    [data-testid="stSidebarUserContent"] {
        direction: rtl !important;
        text-align: right !important;
    }
    
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] p {
        color: #0F172A !important;
    }
    
    [data-testid="stSidebar"] hr { 
        border-color: #E2E8F0 !important; 
    }

    button[data-testid="stSidebarCollapseButton"] {
        background-color: #FFFFFF !important;
        border-radius: 50% !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.08) !important;
        border: 1px solid #E2E8F0 !important;
        color: #1B2559 !important;
        direction: ltr !important; 
    }

    /* 6. باقي تنسيقات النظام */
    .erp-card { background: #FFFFFF; border-radius: 20px; padding: 30px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.03); border: 1px solid #E2E8F0 !important; margin-bottom: 25px; direction: rtl !important; }
    .top-navbar { display: flex; justify-content: space-between; align-items: center; background: #FFFFFF; padding: 20px 30px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.03); margin-bottom: 30px; direction: rtl; border: 1px solid #E2E8F0; }
    .top-navbar-titles h2 { margin: 0; color: #1B2559; font-weight: 800; font-size: 26px; }
    .top-navbar-titles p { margin: 0; color: #64748B; font-size: 14px; font-weight: 600; margin-top: 4px; }
    .top-navbar-date { background: #F4F7FE; color: #4318FF; padding: 10px 20px; border-radius: 50px; font-weight: 800; font-size: 14px; display: flex; align-items: center; gap: 8px; direction: rtl;}

    .summary-card { background: #FFFFFF; padding: 25px; border-radius: 20px; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.03); margin-bottom: 20px; border-bottom: 4px solid #4318FF; border: 1px solid #E2E8F0;}
    .summary-card h3 { margin: 0; font-size: 14px; color: #64748B; font-family: 'Cairo'; font-weight: 700;}
    .summary-card h2 { margin: 10px 0 0 0; font-size: 28px; font-weight: 800; color: #1B2559; font-family: 'Tajawal';}
    .summary-card.danger { border-bottom-color: #EE5D50; }
    .summary-card.danger h2 { color: #EE5D50; }

    .modern-table-wrapper { overflow-x: auto; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.03); margin-bottom: 20px; background: white; border: 1px solid #E2E8F0;}
    .modern-table { width: 100%; border-collapse: collapse; text-align: center; direction: rtl;}
    .modern-table th { background-color: #F8FAFC; color: #1B2559; font-weight: 800; font-size: 13px; padding: 18px 15px; border-bottom: 1px solid #E2E8F0; text-transform: uppercase; }
    .modern-table td { padding: 16px 15px; color: #475569; font-weight: 700; font-size: 14px; border-bottom: 1px solid #E2E8F0; vertical-align: middle; white-space: nowrap; transition: background 0.2s; }
    .modern-table tbody tr:hover td { background-color: #F1F5F9; }

    .stButton>button { border-radius: 12px !important; font-weight: 800 !important; font-family: 'Cairo', sans-serif !important; transition: all 0.3s ease !important; }
    button[data-testid="baseButton-primary"] { background: linear-gradient(135deg, #4318FF 0%, #3B82F6 100%) !important; color: white !important; border: none !important; box-shadow: 0 4px 15px rgba(67, 24, 255, 0.2) !important; }
    button[data-testid="baseButton-primary"]:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(67, 24, 255, 0.4) !important; }
    
    .status-badge { padding: 8px 16px; border-radius: 30px; font-size: 12px; font-weight: 800; display: inline-block; text-align: center;}
    .status-danger { background-color: #FEE2E2; color: #EE5D50; }
    .status-warning { background-color: #FEF3C7; color: #D97706; }
    .status-success { background-color: #E0F2FE; color: #0284C7; } 
    .status-none { background-color: #F1F5F9; color: #64748B; }

    div[data-testid="stDataFrame"] { direction: rtl !important; }
    div[data-baseweb="popover"] { z-index: 999999 !important; }
    div[data-baseweb="calendar"] { padding-top: 10px !important; direction: ltr !important; } 
    
    /* تصميم شبكة التنبيهات */
    .alerts-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); 
        gap: 15px;
        margin-top: 15px;
        direction: rtl;
    }
    .alert-card-compact {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px;
        display: flex;
        align-items: center;
        gap: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.02);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .alert-card-compact:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.08);
    }
    .alert-icon-box {
        width: 45px;
        height: 45px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        flex-shrink: 0;
    }
    .alert-text-box {
        display: flex;
        flex-direction: column;
        gap: 4px;
    }
    .alert-title-text {
        color: #1B2559;
        font-size: 13px;
        font-weight: 700;
        line-height: 1.5;
    }
    .alert-date-text {
        color: #64748B;
        font-size: 12px;
        font-weight: 600;
    }
    .alert-date-text span {
        font-weight: 800;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. إدارة حالة تسجيل الدخول والكوكيز واستعادة كلمة المرور
# ==========================================
saved_user_id = cookie_manager.get("ak_erp_user_id")
saved_user_name = cookie_manager.get("ak_erp_user_name")

if saved_user_id and str(saved_user_id) != "None":
    try:
        st.session_state["user_id"] = int(saved_user_id)
        st.session_state["user_name"] = str(saved_user_name) if saved_user_name else ""
    except Exception:
        if "user_id" not in st.session_state: st.session_state["user_id"] = None
        if "user_name" not in st.session_state: st.session_state["user_name"] = ""
else:
    if "user_id" not in st.session_state: st.session_state["user_id"] = None
    if "user_name" not in st.session_state: st.session_state["user_name"] = ""

if "reset_step" not in st.session_state:
    st.session_state.reset_step = 0

if st.session_state["user_id"] is None:
    st.sidebar.title("نظام A.K (ERP)")
    auth_choice = st.sidebar.radio("بوابة الدخول", ["تسجيل الدخول", "إنشاء حساب جديد كلياً"])
    
    if auth_choice == "إنشاء حساب جديد كلياً":
        st.subheader("تسجيل حساب شركة جديد")
        new_company = st.text_input("اسم الشركة")
        new_phone = st.text_input("رقم الجوال")
        new_email = st.text_input("البريد الإلكتروني")
        new_password = st.text_input("كلمة المرور", type="password")
        
        if st.button("تسجيل الحساب"):
            data = {
                "full_name": new_company,
                "phone": new_phone,
                "email": new_email.strip(),
                "password": new_password
            }
            try:
                response = requests.post(f"{API_URL}/register", json=data)
                if response.status_code == 200:
                    st.success("تم تسجيل الحساب بنجاح! يمكنك الانتقال لتسجيل الدخول.")
                else:
                    error_msg = response.json().get("detail", "حدث خطأ أثناء التسجيل")
                    st.error(error_msg)
            except requests.exceptions.ConnectionError:
                st.error("فشل الاتصال بالسيرفر. يرجى التأكد من تشغيل السيرفر الخلفي.")

    elif auth_choice == "تسجيل الدخول":
        st.subheader("تسجيل الدخول إلى حسابك")
        
        if st.session_state.reset_step == 0:
            login_email = st.text_input("البريد الإلكتروني").strip()
            login_password = st.text_input("كلمة المرور", type="password")
            remember_me = st.checkbox("تذكرني (البقاء مسجلاً للدخول)")
            
            if st.button("دخول"):
                data = {"email": login_email, "password": login_password}
                try:
                    response = requests.post(f"{API_URL}/login", json=data)
                    if response.status_code == 200:
                        res_data = response.json()
                        st.session_state["user_id"] = res_data.get("id", 1) 
                        fetched_name = res_data.get("name")
                        st.session_state["user_name"] = str(fetched_name) if fetched_name else login_email
                        
                        if remember_me:
                            expire_date = datetime.datetime.now() + datetime.timedelta(days=30)
                            cookie_manager.set("ak_erp_user_id", str(st.session_state["user_id"]), expires_at=expire_date)
                            cookie_manager.set("ak_erp_user_name", st.session_state["user_name"], expires_at=expire_date)
                            
                        st.success("تم تسجيل الدخول بنجاح!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("البريد الإلكتروني أو كلمة المرور غير صحيحة")
                except requests.exceptions.ConnectionError:
                    st.error("فشل الاتصال بالسيرفر.")
            
            st.markdown("---")
            if st.button("نسيت كلمة المرور؟"):
                st.session_state.reset_step = 1
                st.rerun()

        elif st.session_state.reset_step == 1:
            st.info("أدخل بريدك الإلكتروني المسجل لإرسال رمز التحقق (OTP)")
            reset_email = st.text_input("البريد الإلكتروني المسجل", key="reset_email_input").strip()
            col1, col2 = st.columns(2)
            with col1:
                if st.button("إرسال الرمز"):
                    try:
                        response = requests.post(f"{API_URL}/forgot-password", json={"email": reset_email})
                        if response.status_code == 200:
                            st.success("تم إرسال الرمز إلى بريدك بنجاح.")
                            st.session_state.reset_email = reset_email
                            st.session_state.reset_step = 2
                            st.rerun()
                        else:
                            st.error("البريد الإلكتروني غير مسجل في النظام.")
                    except requests.exceptions.ConnectionError:
                        st.error("فشل الاتصال بالسيرفر.")
            with col2:
                if st.button("العودة لتسجيل الدخول"):
                    st.session_state.reset_step = 0
                    st.rerun()

        elif st.session_state.reset_step == 2:
            st.info(f"تم إرسال الرمز إلى: {st.session_state.reset_email}")
            otp_code = st.text_input("رمز التحقق (OTP)")
            new_pass = st.text_input("كلمة المرور الجديدة", type="password")
            confirm_pass = st.text_input("تأكيد كلمة المرور", type="password")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("تغيير كلمة المرور"):
                    if new_pass != confirm_pass:
                        st.error("كلمتا المرور غير متطابقتين")
                    elif not otp_code:
                        st.error("الرجاء إدخال رمز التحقق")
                    else:
                        data = {"email": st.session_state.reset_email, "otp": otp_code, "new_password": new_pass}
                        try:
                            response = requests.post(f"{API_URL}/reset-password", json=data)
                            if response.status_code == 200:
                                st.success("تم تغيير كلمة المرور بنجاح! يمكنك الآن تسجيل الدخول.")
                                st.session_state.reset_step = 0
                                st.rerun()
                            else:
                                st.error(response.json().get("detail", "رمز التحقق غير صحيح أو منتهي الصلاحية"))
                        except requests.exceptions.ConnectionError:
                            st.error("فشل الاتصال بالسيرفر.")
            with col2:
                if st.button("إلغاء"):
                    st.session_state.reset_step = 0
                    st.rerun()
    st.stop()

# ==========================================
# 3. الدوال المساعدة
# ==========================================
UID = st.session_state["user_id"]

def get_hijri_date_str(greg_date=None):
    if not greg_date: greg_date = date.today()
    if HAS_HIJRI: return f"{Gregorian(greg_date.year, greg_date.month, greg_date.day).to_hijri().year}-{Gregorian(greg_date.year, greg_date.month, greg_date.day).to_hijri().month:02d}-{Gregorian(greg_date.year, greg_date.month, greg_date.day).to_hijri().day:02d}"
    return "غير متاح"

def clean_none(val):
    if pd.isnull(val) or str(val) == "None": return ""
    return str(val) if str(val) != "لا يوجد" else ""

def display_clean(val):
    if pd.isnull(val) or str(val) == "None" or str(val).strip() == "": return "لا يوجد"
    return str(val)

def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months; year = sourcedate.year + month // 12
    month = month % 12 + 1; day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)

def fetch_data(endpoint):
    try:
        res = requests.get(f"{API_URL}/{endpoint}?t={time.time()}")
        if res.status_code == 200: return res.json()
    except: return []
    return []

sys_settings = fetch_data(f"settings/{UID}")
if not sys_settings: sys_settings = {}

def format_status(date_val, section_name):
    try:
        if pd.isnull(date_val) or str(date_val).strip() == "" or str(date_val) == "None" or str(date_val) == "لا يوجد": return "<div class='status-badge status-none'>لا يوجد</div>"
        days = (pd.to_datetime(date_val).date() - date.today()).days
        w = sys_settings.get(section_name, {}).get("warning_days", 30)
        d = sys_settings.get(section_name, {}).get("danger_days", 0)
        if days <= d: return f"<div class='status-badge status-danger'>حرج ({abs(days)} يوم)</div>"
        elif days <= w: return f"<div class='status-badge status-warning'>تحذير ({days} يوم)</div>"
        else: return f"<div class='status-badge status-success'>ساري ({days} يوم)</div>"
    except: return "<div class='status-badge status-none'>خطأ</div>"

def custom_date_picker(label_prefix, default_date=None, key_suffix=""):
    st.markdown(f"<div style='font-size:14px; font-weight:800; color:#1B2559; margin-bottom:8px; text-align:right;'>{label_prefix}</div>", unsafe_allow_html=True)
    c_check, c_date = st.columns([1, 4])
    is_none = c_check.checkbox("لا يوجد", key=f"none_{label_prefix}_{key_suffix}", value=(default_date is None or pd.isnull(default_date)))
    if is_none:
        with c_date: st.info("تم اختيار 'لا يوجد تاريخ'")
        return None
    else:
        if default_date is None or pd.isnull(default_date): start_val = date.today()
        elif isinstance(default_date, str):
            try: start_val = pd.to_datetime(default_date).date()
            except: start_val = date.today()
        else: start_val = default_date
        with c_date:
            c1, c2, c3 = st.columns([1, 1, 1.5])
            y_list = list(range(1990, 2051)); m_list = list(range(1, 13))
            safe_y = start_val.year if start_val.year in y_list else date.today().year
            with c1: day = st.selectbox("يوم", list(range(1, 32)), index=start_val.day - 1, key=f"d_{label_prefix}_{key_suffix}")
            with c2: month = st.selectbox("شهر", m_list, index=start_val.month - 1, key=f"m_{label_prefix}_{key_suffix}")
            with c3: year = st.selectbox("سنة", y_list, index=y_list.index(safe_y), key=f"y_{label_prefix}_{key_suffix}")
            try: return date(year, month, day)
            except ValueError: return date(year, month, calendar.monthrange(year, month)[1])

def calculate_visa_expiry(travel_date, months, days, extensions):
    if not travel_date: return None
    try: m = int(months) if str(months).strip() and str(months).isdigit() else 0; d = int(days) if str(days).strip() and str(days).isdigit() else 0; ext = int(extensions) if str(extensions).strip() and str(extensions).isdigit() else 0
    except: return None
    total_months = m + ext
    if HAS_HIJRI:
        h_date = Gregorian(travel_date.year, travel_date.month, travel_date.day).to_hijri(); new_month = h_date.month + total_months; new_year = h_date.year
        while new_month > 12: new_month -= 12; new_year += 1
        try: base_g = Hijri(new_year, new_month, h_date.day).to_gregorian()
        except OverflowError: base_g = Hijri(new_year, new_month, 29).to_gregorian()
        from datetime import timedelta
        return date(base_g.year, base_g.month, base_g.day) + timedelta(days=d)
    else:
        from datetime import timedelta
        return travel_date + timedelta(days=(total_months * 30) + d)

def prepare_export_df(df, selected_sub):
    if df.empty: return df
    export_df = df.copy()
    def c_days(date_val):
        if pd.isnull(date_val) or str(date_val).strip() in ["", "None", "لا يوجد"]: return "لا يوجد"
        try: return str((pd.to_datetime(date_val).date() - date.today()).days)
        except: return "لا يوجد"
    def c_val(val):
        if pd.isnull(val) or str(val) in ["None", ""] or str(val).strip() == "": return "لا يوجد"
        return str(val)
    for col in export_df.columns: export_df[col] = export_df[col].apply(c_val)

    if selected_sub == "الموظفين":
        export_df["أيام متبقية (إقامة)"] = export_df["iqama_expiry"].apply(c_days)
        export_df["أيام متبقية (تأمين)"] = export_df["health_insurance_expiry"].apply(c_days)
        export_df["أيام متبقية (جواز)"] = export_df["passport_expiry"].apply(c_days)
        export_df = export_df.rename(columns={"id": "م", "name": "اسم الموظف", "iqama_number": "رقم الإقامة", "iqama_expiry": "تاريخ الانتهاء", "health_insurance_expiry": "انتهاء التأمين", "sponsorship": "الكفالة", "passport_expiry": "انتهاء الجواز"})
        return export_df[["م", "اسم الموظف", "رقم الإقامة", "تاريخ الانتهاء", "أيام متبقية (إقامة)", "انتهاء التأمين", "أيام متبقية (تأمين)", "الكفالة", "انتهاء الجواز", "أيام متبقية (جواز)"]]
    elif selected_sub == "السيارات":
        export_df["ايام متبقية"] = export_df["registration_expiry"].apply(c_days)
        export_df["ايام متبقية "] = export_df["insurance_expiry"].apply(c_days)
        export_df = export_df.rename(columns={"id": "م", "car_name": "اسم السيارة", "plate_number": "رقم اللوحة", "registration_number": "رقم الاستمارة", "registration_expiry": "تاريخ انتهاء الاستمارة", "insurance_expiry": "تاريخ انتهاء التامين"})
        return export_df[["م", "اسم السيارة", "رقم اللوحة", "رقم الاستمارة", "تاريخ انتهاء الاستمارة", "ايام متبقية", "تاريخ انتهاء التامين", "ايام متبقية "]]
    elif selected_sub == "التأشيرات":
        export_df["الايام المتبقية"] = export_df["expiry_date"].apply(c_days)
        export_df = export_df.rename(columns={"id": "م", "employee_name": "الاسم", "visa_number": "رقم التاشيرة", "travel_date": "تاريخ السفر", "visa_duration_months": "مدة التاشيرة بالاشهر", "visa_duration_days": "مدة التاشيرة بالايام", "extension_count": "عدد التمديدات", "expiry_date": "تاريخ انتهاء التاشيرة", "notes": "ملاحظات"})
        return export_df[["م", "الاسم", "رقم التاشيرة", "تاريخ السفر", "مدة التاشيرة بالاشهر", "مدة التاشيرة بالايام", "عدد التمديدات", "تاريخ انتهاء التاشيرة", "الايام المتبقية", "ملاحظات"]]
    elif selected_sub == "عقود الإيجار":
        export_df["الايام المتبقية"] = export_df["contract_expiry"].apply(c_days)
        export_df = export_df.rename(columns={"id": "م", "tenant_name": "اسم المستاجر", "apartment_number": "رقم الشقة", "contract_number": "رقم العقد", "contract_start_date": "تاريخ بداية العقد", "contract_duration": "مدة العقد", "contract_expiry": "تاريخ انتهاء العقد", "next_payment_date": "تاريخ الدفعة القادمة", "payment_amount": "مبلغ الدفعة", "payment_period_months": "فترة الدفع بالشهر", "annual_rent": "مبلغ الايجار السنوي"})
        return export_df[["م", "اسم المستاجر", "رقم الشقة", "رقم العقد", "تاريخ بداية العقد", "مدة العقد", "تاريخ انتهاء العقد", "الايام المتبقية", "تاريخ الدفعة القادمة", "مبلغ الدفعة", "فترة الدفع بالشهر", "مبلغ الايجار السنوي"]]
    elif selected_sub == "الاشتراكات العامة":
        export_df["ايام متبقية"] = export_df["subscription_expiry"].apply(c_days)
        export_df = export_df.rename(columns={"id": "م", "service_name": "اسم الاشتراك او الترخيص", "subscription_number": "الرقم", "subscription_expiry": "تاريخ الانتهاء", "notes": "ملاحظات"})
        return export_df[["م", "اسم الاشتراك او الترخيص", "الرقم", "تاريخ الانتهاء", "ايام متبقية", "ملاحظات"]]
    return export_df

def to_excel(df, sheet_name="البيانات"):
    df_clean = df.replace({np.nan: "", None: ""}).astype(str)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_clean.to_excel(writer, index=False, sheet_name=sheet_name)
        workbook = writer.book
        worksheet = writer.sheets[sheet_name]
        worksheet.right_to_left()
        header_format = workbook.add_format({'bold': True, 'valign': 'center', 'align': 'center', 'fg_color': '#1B2559', 'font_color': 'white', 'border': 1, 'font_name': 'Tahoma', 'font_size': 11})
        cell_format = workbook.add_format({'valign': 'center', 'align': 'center', 'border': 1, 'font_name': 'Tahoma', 'font_size': 10})
        for col_num, value in enumerate(df_clean.columns.values):
            worksheet.write(0, col_num, value, header_format)
            try: column_len = max(df_clean[value].map(lambda x: len(str(x))).max(), len(str(value))) + 6
            except: column_len = 15
            worksheet.set_column(col_num, col_num, column_len, cell_format)
    return output.getvalue()

def to_pdf_html_basic(df, title):
    h_date = get_hijri_date_str()
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head><meta charset="UTF-8"><title>تقرير - A.K ERP</title>
    <style>@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;800&display=swap'); body {{ font-family: 'Cairo', sans-serif; padding: 20px; direction: rtl; text-align:right;}} .header {{ text-align: center; margin-bottom: 20px; }} table {{ width: 100%; border-collapse: collapse; margin-top: 15px; text-align: center; direction:rtl;}} th, td {{ padding: 12px; border: 1px solid #E9EDF7; }} th {{ background-color: #1E293B !important; color: #FFFFFF !important; font-weight: bold; -webkit-print-color-adjust: exact; color-adjust: exact; }} tr:nth-child(even) {{ background-color: #F8FAFC !important; -webkit-print-color-adjust: exact; color-adjust: exact; }} .print-btn {{ padding: 10px 20px; background: #2563EB; color: white; border: none; border-radius: 6px; cursor: pointer; display: block; margin: auto; }} @media print {{ .no-print {{ display: none !important; }} }}</style>
    </head><body>
    <button onclick="window.print()" class="print-btn no-print">🖨️ للطباعة</button>
    <div class="header"><h2 style="color:#4318FF;">A.K ERP System</h2><h3>{title}</h3><p>الميلادي: {date.today().strftime('%Y-%m-%d')} | الهجري: {h_date}هـ</p></div>
    {df.to_html(index=False, classes='modern-table', border=0)}
    </body></html>"""
    return html_content.encode('utf-8')

def to_pdf_html_with_dashboard(df, title, g_total=None, g_paid=None, g_rem=None, g_late=None):
    h_date = get_hijri_date_str()
    dashboard_html = ""
    if g_total is not None:
        dashboard_html = f"""
        <div style="display:flex; justify-content:space-around; background:#F8FAFC; padding:15px; border-radius:10px; border:1px solid #E2E8F0; margin-bottom:20px;">
            <div style="text-align:center;"><b>إجمالي مبلغ التقسيط</b><br><span style="color:#1B2559; font-size:18px;">{g_total:,.2f}</span></div>
            <div style="text-align:center;"><b>إجمالي المبلغ المسدد</b><br><span style="color:#0284C7; font-size:18px;">{g_paid:,.2f}</span></div>
            <div style="text-align:center;"><b>إجمالي المبالغ المتبقية</b><br><span style="color:#D97706; font-size:18px;">{g_rem:,.2f}</span></div>
            <div style="text-align:center;"><b>إجمالي المبالغ المتأخرة</b><br><span style="color:#EE5D50; font-size:18px;">{g_late:,.2f}</span></div>
        </div>
        """
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head><meta charset="UTF-8"><title>تقرير أقساط - A.K ERP</title>
    <style>@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;800&display=swap'); body {{ font-family: 'Cairo', sans-serif; padding: 20px; direction: rtl; text-align:right;}} .header {{ text-align: center; margin-bottom: 20px; }} table {{ width: 100%; border-collapse: collapse; margin-top: 15px; text-align: center; direction:rtl;}} th, td {{ padding: 12px; border: 1px solid #E9EDF7; }} th {{ background-color: #1E293B !important; color: #FFFFFF !important; font-weight: bold; -webkit-print-color-adjust: exact; color-adjust: exact; }} tr:nth-child(even) {{ background-color: #F8FAFC !important; -webkit-print-color-adjust: exact; color-adjust: exact; }} .print-btn {{ padding: 10px 20px; background: #2563EB; color: white; border: none; border-radius: 6px; cursor: pointer; display: block; margin: auto; }} @media print {{ .no-print {{ display: none !important; }} }}</style>
    </head><body>
    <button onclick="window.print()" class="print-btn no-print">🖨️ للطباعة</button>
    <div class="header"><h2 style="color:#4318FF;">A.K ERP System</h2><h3>{title}</h3><p>الميلادي: {date.today().strftime('%Y-%m-%d')} | الهجري: {h_date}هـ</p></div>
    {dashboard_html}
    {df.to_html(index=False, classes='modern-table', border=0)}
    </body></html>"""
    return html_content.encode('utf-8')

# ==========================================
# 4. بناء القائمة الجانبية
# ==========================================
if "current_nav" not in st.session_state: st.session_state.current_nav = "لوحة القيادة"
if "sub_expanded" not in st.session_state: st.session_state.sub_expanded = False
if "payroll_expanded" not in st.session_state: st.session_state.payroll_expanded = False

with st.sidebar:
    user_name_display = str(st.session_state.get("user_name", ""))
    st.markdown(f"""
        <div style="text-align: center; padding: 20px 0 10px 0;">
            <div style="background: linear-gradient(135deg, #4318FF, #3B82F6); display:inline-block; padding:15px; border-radius:15px; margin-bottom:10px; box-shadow: 0 4px 15px rgba(67, 24, 255, 0.4);">
                <h1 style="color: #FFFFFF; margin:0; font-size:2.5rem; line-height:1;">A.K</h1>
            </div>
            <h2 style="color: #0F172A; font-family:'Cairo'; font-weight:800; margin:0; font-size: 1.6rem; letter-spacing: 1px;">ERP SYSTEM</h2>
            <p style="color: #64748B; font-size:12px; margin-top:5px; font-weight:700;">المساحة السحابية: {user_name_display}</p>
            <hr style="border-color: #E2E8F0; margin: 20px 10px 10px 10px;">
        </div>
    """, unsafe_allow_html=True)
    
    menu_options = ["لوحة القيادة"]
    menu_icons = ["house-fill"]

    if st.session_state.sub_expanded:
        menu_options.append("المتابعة الشاملة ⏷")
        menu_icons.append("folder2-open")
        menu_options.extend(["   🔹 الموظفين", "   🔹 السيارات", "   🔹 التأشيرات", "   🔹 عقود الإيجار", "   🔹 الاشتراكات العامة"])
        menu_icons.extend(["dash", "dash", "dash", "dash", "dash"])
    else:
        menu_options.append("المتابعة الشاملة ⏴")
        menu_icons.append("folder")
        
    if st.session_state.payroll_expanded:
        menu_options.append("نظام الرواتب ⏷")
        menu_icons.append("cash-stack")
        menu_options.extend(["   🔹 كشف الرواتب", "   🔹 حركة وسلف", "   🔹 راتب مساند", "   🔹 التقرير السنوي"])
        menu_icons.extend(["dash", "dash", "dash", "dash"])
    else:
        menu_options.append("نظام الرواتب ⏴")
        menu_icons.append("cash-coin")

    menu_options.extend(["بيانات المدير", "بيانات العمال", "جداول إضافية", "إدارة الأقساط", "محول التاريخ", "الإعدادات"])
    
    # 🚨 تم تصحيح اسم أيقونة "محول التاريخ" هنا لتجنب انهيار مكتبة option_menu 🚨
    menu_icons.extend(["person-badge-fill", "people-fill", "clipboard-data", "credit-card", "calendar3", "gear-fill"])
    
    try: def_idx = menu_options.index(st.session_state.current_nav)
    except ValueError: def_idx = 0

    selected_item = option_menu(
        "القائمة الرئيسية", 
        options=menu_options,
        icons=menu_icons,
        default_index=def_idx,
        styles={
            "container": {"background-color": "transparent", "padding": "0", "border": "none"},
            "icon": {"color": "#3B82F6", "font-size": "18px"}, 
            "nav-link": {
                "color": "#0F172A", 
                "font-size": "15px", 
                "font-family": "Cairo", 
                "font-weight": "700", 
                "margin":"4px 0", 
                "text-align": "right", 
                "border-radius": "8px", 
                "transition": "all 0.3s"
            },
            "nav-link-selected": {
                "background-color": "#2563EB", 
                "color": "#FFFFFF", 
                "font-weight": "800"
            }
        }
    )

    st.markdown("<hr style='border-color: #E2E8F0; margin: 20px 10px;'>", unsafe_allow_html=True)
    if st.button("🚪 تسجيل الخروج", use_container_width=True):
        st.session_state["user_id"] = None
        st.session_state["user_name"] = ""
        try:
            cookie_manager.delete("ak_erp_user_id")
            cookie_manager.delete("ak_erp_user_name")
        except:
            pass
        st.rerun()

if selected_item and selected_item != st.session_state.current_nav:
    if selected_item == "المتابعة الشاملة ⏴": st.session_state.sub_expanded = True; st.session_state.current_nav = "   🔹 الموظفين"
    elif selected_item == "المتابعة الشاملة ⏷": st.session_state.sub_expanded = False; st.session_state.current_nav = "لوحة القيادة"
    elif selected_item == "نظام الرواتب ⏴": st.session_state.payroll_expanded = True; st.session_state.current_nav = "   🔹 كشف الرواتب"
    elif selected_item == "نظام الرواتب ⏷": st.session_state.payroll_expanded = False; st.session_state.current_nav = "لوحة القيادة"
    else:
        st.session_state.sub_expanded = "🔹" in selected_item and selected_item in ["   🔹 الموظفين", "   🔹 السيارات", "   🔹 التأشيرات", "   🔹 عقود الإيجار", "   🔹 الاشتراكات العامة"]
        st.session_state.payroll_expanded = "🔹" in selected_item and selected_item in ["   🔹 كشف الرواتب", "   🔹 حركة وسلف", "   🔹 راتب مساند", "   🔹 التقرير السنوي"]
        st.session_state.current_nav = selected_item
    st.rerun()

actual_selection = st.session_state.current_nav.replace("   🔹 ", "").replace(" ⏷", "").replace(" ⏴", "")
main_menu = actual_selection
selected_sub = None

if actual_selection in ["الموظفين", "السيارات", "التأشيرات", "عقود الإيجار", "الاشتراكات العامة"]:
    main_menu = "المتابعة الشاملة"
    selected_sub = actual_selection
elif actual_selection in ["كشف الرواتب", "حركة وسلف", "راتب مساند", "التقرير السنوي"]:
    main_menu = "نظام الرواتب"
    selected_sub = actual_selection

def render_delete_notification(endpoint_name):
    if 'pending_delete' in st.session_state and st.session_state['pending_delete']['endpoint'] == endpoint_name:
        del_info = st.session_state['pending_delete']
        elapsed = int(time.time() - del_info['time'])
        rem = 10 - elapsed
        st.markdown("<div class='erp-card' style='border: 2px solid #EE5D50; background-color: #FFF0F0;'>", unsafe_allow_html=True)
        if rem > 0:
            st.markdown(f"<h3 style='color:#EE5D50; text-align:center;'>⚠ جاري حذف السجل نهائياً خلال {rem} ثواني...</h3>", unsafe_allow_html=True)
            if st.button("🛑 تخطي وإلغاء الحذف", type="primary", use_container_width=True): del st.session_state['pending_delete']; st.rerun()
            time.sleep(1); st.rerun()
        else:
            requests.delete(f"{API_URL}/{del_info['endpoint']}/{del_info['id']}/{UID}")
            del st.session_state['pending_delete']
            st.markdown(f"<h3 style='color:#059669; text-align:center;'>✅ تم الحذف بنجاح!</h3>", unsafe_allow_html=True)
            time.sleep(1); st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

def render_top_navbar(title, subtitle):
    g_date = date.today().strftime('%Y-%m-%d'); h_date = get_hijri_date_str()
    st.markdown(f"""
        <div class="top-navbar">
            <div class="top-navbar-date">📅 الميلادي: <b>{g_date}</b> &nbsp;|&nbsp; الهجري: <b>{h_date}هـ</b></div>
            <div class="top-navbar-titles"><h2>{title}</h2><p>{subtitle}</p></div>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# 6. التوجيه وعرض الواجهة الرئيسية
# ==========================================

if main_menu == "لوحة القيادة":
    render_top_navbar("لوحة القيادة 📊", "نظرة عامة على التنبيهات وحالة النظام")
    data = fetch_data(f"api/daily-report/{UID}")
    alerts = data.get("التفاصيل", []) if isinstance(data, dict) else []
    if alerts:
        grid_html = '<div class="alerts-grid">'
        for alert in alerts:
            status = alert.get("الحالة", "")
            title = alert.get("البيان", "")
            exp_date = alert.get("تاريخ_الانتهاء", "")
            days = alert.get("الايام_المتبقية", 0)
            
            if status == "حرج":
                border_color = "#EE5D50" 
                bg_color = "#FEE2E2"
                text_color = "#EE5D50"
                icon = "🚨"
            else:
                border_color = "#D97706"  
                bg_color = "#FEF3C7"
                text_color = "#D97706"
                icon = "⚠️"
            
            grid_html += f"""<div class="alert-card-compact" style="border-right: 5px solid {border_color};">
<div class="alert-icon-box" style="background-color: {bg_color};">{icon}</div>
<div class="alert-text-box">
<div class="alert-title-text">{title}</div>
<div class="alert-date-text">ينتهي في: <span style="color: {text_color};">{exp_date}</span> (متبقي {days} يوم)</div>
</div>
</div>"""
        grid_html += '</div>'
        st.markdown(grid_html, unsafe_allow_html=True)
    else:
        st.success("🎉 لا توجد أي تنبيهات حالياً. كل الأمور ممتازة!")

elif main_menu == "محول التاريخ":
    render_top_navbar("محول التاريخ 🔄", "تحويل دقيق ومباشر بين التاريخ الميلادي والهجري")
    if not HAS_HIJRI: st.error("مكتبة التحويل غير مثبتة.")
    else:
        st.markdown("<div class='erp-card'>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c2:
            st.markdown("<h4 style='color:#2563EB; font-weight:800;'>من ميلادي إلى هجري</h4>", unsafe_allow_html=True)
            g_date = st.date_input("اختر التاريخ الميلادي:", value=date.today())
            if st.button("تحويل للهجري", type="primary", use_container_width=True):
                h_result = Gregorian(g_date.year, g_date.month, g_date.day).to_hijri()
                st.success(f"يوافق بالهجري: {h_result.year}-{h_result.month:02d}-{h_result.day:02d} هـ")
        with c1:
            st.markdown("<h4 style='color:#2563EB; font-weight:800;'>من هجري إلى ميلادي</h4>", unsafe_allow_html=True)
            today_h = Gregorian.today().to_hijri()
            cc1, cc2, cc3 = st.columns(3)
            with cc3: h_y = st.number_input("السنة", min_value=1300, max_value=1500, value=today_h.year)
            with cc2: h_m = st.number_input("الشهر", min_value=1, max_value=12, value=today_h.month)
            with cc1: h_d = st.number_input("اليوم", min_value=1, max_value=30, value=today_h.day)
            if st.button("تحويل للميلادي", type="primary", use_container_width=True):
                try:
                    g_result = Hijri(h_y, h_m, h_d).to_gregorian()
                    st.success(f"يوافق بالميلادي: {g_result.strftime('%Y-%m-%d')} م")
                except OverflowError: st.error("تاريخ هجري غير صحيح.")
        st.markdown("</div>", unsafe_allow_html=True)

elif main_menu == "نظام الرواتب" and selected_sub:
    render_top_navbar(f"{selected_sub}", "حسابات دقيقة وتفاعلية مرنة")
    
    if selected_sub == "كشف الرواتب":
        st.markdown("<div class='erp-card'>", unsafe_allow_html=True)
        c_y, c_m = st.columns([1, 2])
        curr_y = date.today().year
        with c_y: p_year = st.number_input("السنة:", min_value=2000, value=curr_y)
        with c_m: p_month = st.selectbox("اختر الشهر:", ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"])
        st.markdown("</div>", unsafe_allow_html=True)
        
        raw_payroll = fetch_data(f"payroll/{p_year}/{p_month}/{UID}")
        cols = ["م", "اسم الموظف", "حالة السفر", "متأخر ٥", "متأخر ٦", "متأخر ٧", "متأخر ٨", "راتب الشهر", "السلف", "قيمة الغياب", "مدد", "مساند", "إجمالي الاستقطاعات", "الصافي", "استلم", "المتبقي للترحيل", "سند"]
        df_pay = pd.DataFrame(raw_payroll) if raw_payroll else pd.DataFrame(columns=cols)
        for col in cols:
            if col not in df_pay.columns: df_pay[col] = ""
            
        st.markdown("<h4 style='color:#1E293B; font-weight:800; margin-bottom:15px;'>قم بإدخال البيانات واضغط حفظ ليتم الحساب التلقائي للاستقطاعات والصافي:</h4>", unsafe_allow_html=True)
        
        edited_df = st.data_editor(
            df_pay[cols[::-1]], 
            num_rows="dynamic", use_container_width=True, hide_index=True, key=f"pay_{p_year}_{p_month}",
            column_config={
                "م": st.column_config.TextColumn(),
                "إجمالي الاستقطاعات": st.column_config.NumberColumn(disabled=True, format="%.2f"),
                "الصافي": st.column_config.NumberColumn(disabled=True, format="%.2f"),
                "المتبقي للترحيل": st.column_config.NumberColumn(disabled=True, format="%.2f"),
                "حالة السفر": st.column_config.SelectboxColumn(options=["على رأس العمل", "مسافر", "إجازة", "منقطع", "-"]),
                "راتب الشهر": st.column_config.NumberColumn(format="%.2f"),
                "السلف": st.column_config.NumberColumn(format="%.2f"),
                "قيمة الغياب": st.column_config.NumberColumn(format="%.2f"),
                "مدد": st.column_config.NumberColumn(format="%.2f"),
                "مساند": st.column_config.NumberColumn(format="%.2f"),
                "استلم": st.column_config.NumberColumn(format="%.2f"),
            }
        )
        
        c_save, c_print = st.columns([2, 1])
        with c_save:
            if st.button("💾 تجميع وحساب وحفظ كشف الرواتب", type="primary", use_container_width=True):
                work_df = edited_df[cols].copy()
                for c in ["متأخر ٥", "متأخر ٦", "متأخر ٧", "متأخر ٨", "راتب الشهر", "السلف", "قيمة الغياب", "مدد", "مساند", "استلم"]:
                    work_df[c] = pd.to_numeric(work_df[c], errors='coerce').fillna(0)
                work_df["إجمالي الاستقطاعات"] = work_df["السلف"] + work_df["قيمة الغياب"] + work_df["مدد"] + work_df["مساند"]
                work_df["الصافي"] = work_df["راتب الشهر"] - work_df["إجمالي الاستقطاعات"]
                work_df["المتبقي للترحيل"] = work_df["الصافي"] - work_df["استلم"]
                
                save_data = work_df.replace({np.nan: "", None: ""}).astype(str).to_dict(orient="records")
                requests.post(f"{API_URL}/payroll/{p_year}/{p_month}/sync", json={"owner_id": UID, "records": save_data})
                st.success("تم الحساب والحفظ بنجاح!"); time.sleep(0.5); st.rerun()
        with c_print:
             st.download_button("🖨 تصدير PDF", to_pdf_html_basic(edited_df[cols], f"كشف الرواتب - {p_month} {p_year}"), f"payroll_{p_year}_{p_month}.html", mime="text/html", use_container_width=True)

    elif selected_sub == "حركة وسلف":
        st.markdown("<div class='erp-card'>", unsafe_allow_html=True)
        c_y, c_e = st.columns([1, 2])
        with c_y: l_year = st.number_input("السنة:", min_value=2000, value=date.today().year)
        with c_e: l_emp = st.text_input("اسم الموظف للبحث/الإضافة:")
        st.markdown("</div>", unsafe_allow_html=True)
        
        if l_emp:
            raw_loans = fetch_data(f"loans/{l_emp}/{l_year}/{UID}")
            cols = ["شهر", "علية", "له", "بيان"]
            df_loans = pd.DataFrame(raw_loans) if raw_loans else pd.DataFrame(columns=cols)
            if df_loans.empty:
                df_loans["شهر"] = list(range(1, 13))
                df_loans["علية"] = ""; df_loans["له"] = ""; df_loans["بيان"] = ""
            
            st.markdown(f"<h4 style='color:#1E293B; font-weight:800; text-align:center; padding:10px; background:#F8FAFC; border:1px solid #E2E8F0;'>اسم الموظف: {l_emp} | السنة: {l_year}</h4>", unsafe_allow_html=True)
            edited_loans = st.data_editor(
                df_loans[cols[::-1]], num_rows="dynamic", hide_index=True, use_container_width=True, key=f"loan_{l_emp}_{l_year}",
                column_config={"شهر": st.column_config.TextColumn(), "علية": st.column_config.NumberColumn(format="%.2f"), "له": st.column_config.NumberColumn(format="%.2f"), "بيان": st.column_config.TextColumn()}
            )
            
            try: total_aleh = pd.to_numeric(edited_loans['علية'], errors='coerce').sum()
            except: total_aleh = 0
            try: total_lo = pd.to_numeric(edited_loans['له'], errors='coerce').sum()
            except: total_lo = 0
            net = total_lo - total_aleh
            
            st.markdown(f"<div style='text-align:left; font-size:18px; font-weight:bold; color:{'#059669' if net>=0 else '#DC2626'}; padding:10px;'>الصافي الكلي: {net:,.2f}</div>", unsafe_allow_html=True)
            
            c_s, c_p = st.columns([2, 1])
            with c_s:
                if st.button("💾 حفظ السجل", type="primary", use_container_width=True):
                    save_data = edited_loans[cols].replace({np.nan: "", None: ""}).astype(str).to_dict(orient="records")
                    requests.post(f"{API_URL}/loans/{l_emp}/{l_year}/sync", json={"owner_id": UID, "records": save_data})
                    st.success("تم الحفظ!"); time.sleep(0.5); st.rerun()
            with c_p: st.download_button("🖨️ تصدير PDF", to_pdf_html_basic(edited_loans[cols], f"بيان حركة وسلف - {l_emp} ({l_year})"), f"loan_{l_emp}_{l_year}.html", mime="text/html", use_container_width=True)
        else: st.info("الرجاء إدخال اسم الموظف لبدء الإدخال.")

    elif selected_sub == "راتب مساند":
        st.markdown("<div class='erp-card'>", unsafe_allow_html=True)
        s_year = st.number_input("السنة:", min_value=2000, value=date.today().year, key="sy")
        st.markdown("</div>", unsafe_allow_html=True)
        
        raw_supp = fetch_data(f"support_salary/{s_year}/{UID}")
        cols = ["الشهر", "التاريخ", "الراتب", "استلم", "الصافي", "حالة الدفع"]
        df_supp = pd.DataFrame(raw_supp) if raw_supp else pd.DataFrame(columns=cols)
        if df_supp.empty:
            df_supp["الشهر"] = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]
            for c in cols[1:]: df_supp[c] = ""
            
        df_supp['حالة الدفع'] = df_supp['حالة الدفع'].astype(str).str.lower().map({'true': True, '1': True, 'yes': True, 'تم': True}).fillna(False)

        edited_supp = st.data_editor(
            df_supp[cols[::-1]], num_rows="dynamic", hide_index=True, use_container_width=True, key=f"supp_sal_{s_year}",
            column_config={
                "حالة الدفع": st.column_config.CheckboxColumn("تم الدفع ✔️", default=False),
                "الصافي": st.column_config.NumberColumn(disabled=True, format="%.2f"),
                "الراتب": st.column_config.NumberColumn(format="%.2f"),
                "استلم": st.column_config.NumberColumn(format="%.2f"),
            }
        )
        c_s, c_p = st.columns([2, 1])
        with c_s:
            if st.button("💾 تجميع وحساب وحفظ", type="primary", use_container_width=True):
                work_df = edited_supp[cols].copy()
                work_df["الراتب"] = pd.to_numeric(work_df["الراتب"], errors='coerce').fillna(0)
                work_df["استلم"] = pd.to_numeric(work_df["استلم"], errors='coerce').fillna(0)
                work_df["الصافي"] = work_df["الراتب"] - work_df["استلم"]
                save_data = work_df.replace({np.nan: "", None: ""}).astype(str).to_dict(orient="records")
                requests.post(f"{API_URL}/support_salary/{s_year}/sync", json={"owner_id": UID, "records": save_data})
                st.success("تم الحساب والحفظ!"); time.sleep(0.5); st.rerun()
        with c_p: st.download_button("🖨️ PDF", to_pdf_html_basic(edited_supp[cols], f"راتب مساند ({s_year})"), f"supp_{s_year}.html", mime="text/html", use_container_width=True)

    elif selected_sub == "التقرير السنوي":
        st.markdown("<div class='erp-card'>", unsafe_allow_html=True)
        c_y, c_e = st.columns([1, 2])
        with c_y: a_year = st.number_input("السنة:", min_value=2000, value=date.today().year, key="a_y")
        with c_e: a_emp = st.text_input("اسم الموظف المُراد استخراج تقريره:", key="a_e")
        st.markdown("</div>", unsafe_allow_html=True)
        
        if a_emp:
            raw_ann = fetch_data(f"annual_report/{a_emp}/{a_year}/{UID}")
            cols = ["الشهر", "الحالة", "الراتب المستحق", "الإضافي", "إجمالي الاستحقاقات", "السلف", "إجمالي الاستقطاعات-كجدول", "إجمالي الاستقطاعات-المسحوبات", "الصافي", "استلم", "المتبقي للترحيل"]
            df_ann = pd.DataFrame(raw_ann) if raw_ann else pd.DataFrame(columns=cols)
            
            if df_ann.empty:
                df_ann["الشهر"] = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]
                for c in cols[1:]: df_ann[c] = ""
                
            edited_ann = st.data_editor(
                df_ann[cols[::-1]], num_rows="dynamic", hide_index=True, use_container_width=True, key=f"ann_{a_emp}_{a_year}",
                column_config={
                    "إجمالي الاستحقاقات": st.column_config.NumberColumn(disabled=True, format="%.2f"),
                    "الصافي": st.column_config.NumberColumn(disabled=True, format="%.2f"),
                    "المتبقي للترحيل": st.column_config.NumberColumn(disabled=True, format="%.2f"),
                    "الراتب المستحق": st.column_config.NumberColumn(format="%.2f"),
                    "الإضافي": st.column_config.NumberColumn(format="%.2f"),
                    "السلف": st.column_config.NumberColumn(format="%.2f"),
                    "إجمالي الاستقطاعات-كجدول": st.column_config.NumberColumn(format="%.2f"),
                    "إجمالي الاستقطاعات-المسحوبات": st.column_config.NumberColumn(format="%.2f"),
                    "استلم": st.column_config.NumberColumn(format="%.2f"),
                    "الحالة": st.column_config.SelectboxColumn(options=["على رأس العمل", "إجازة", "انقطاع", "-"])
                }
            )
            
            c_s, c_p = st.columns([2, 1])
            with c_s:
                if st.button("💾 تجميع وحساب التقرير", type="primary", use_container_width=True):
                    work_df = edited_ann[cols].copy()
                    for c in ["الراتب المستحق", "الإضافي", "السلف", "إجمالي الاستقطاعات-كجدول", "إجمالي الاستقطاعات-المسحوبات", "استلم"]:
                        work_df[c] = pd.to_numeric(work_df[c], errors='coerce').fillna(0)
                    
                    work_df["إجمالي الاستحقاقات"] = work_df["الراتب المستحق"] + work_df["الإضافي"]
                    work_df["الصافي"] = work_df["إجمالي الاستحقاقات"] - work_df["السلف"] - work_df["إجمالي الاستقطاعات-كجدول"] - work_df["إجمالي الاستقطاعات-المسحوبات"]
                    work_df["المتبقي للترحيل"] = work_df["الصافي"] - work_df["استلم"]
                    
                    save_data = work_df.replace({np.nan: "", None: ""}).astype(str).to_dict(orient="records")
                    requests.post(f"{API_URL}/annual_report/{a_emp}/{a_year}/sync", json={"owner_id": UID, "records": save_data})
                    st.success("تم التجميع والحفظ بنجاح!"); time.sleep(0.5); st.rerun()
            with c_p: st.download_button("🖨️️ PDF", to_pdf_html_basic(edited_ann[cols], f"التقرير السنوي - {a_emp} ({a_year})"), f"ann_{a_emp}_{a_year}.html", mime="text/html", use_container_width=True)
        else: st.info("يرجى إدخال اسم الموظف للعرض.")

elif main_menu == "الإعدادات":
    render_top_navbar("إعدادات النظام ⚙", "التحكم في التنبيهات والألوان والنسخ الاحتياطي")
    
    st.markdown("<div class='erp-card'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#4318FF; font-family:Cairo; font-weight:800; margin-bottom:15px;'>🛡️ النسخة الاحتياطية السحابية</h3>", unsafe_allow_html=True)
    st.info("💡 يمكنك تحميل نسخة احتياطية كاملة من بيانات شركتك (كافة الجداول والأقسام) والاحتفاظ بها محلياً.")
    if st.button("📥 إنشاء وتحميل نسخة احتياطية (JSON)", type="primary"):
        res = requests.get(f"{API_URL}/api/backup/{UID}")
        if res.status_code == 200:
            st.download_button("⬇ اضغط هنا للتحميل الآن", data=json.dumps(res.json(), ensure_ascii=False, indent=4), file_name=f"AK_ERP_Backup_{date.today()}.json", mime="application/json")
        else: st.error("حدث خطأ أثناء جلب النسخة.")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='erp-card'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#4318FF; font-family:Cairo; font-weight:800; margin-bottom:15px;'>🔔 إعدادات التنبيهات</h3>", unsafe_allow_html=True)
    sections = ["الموظفين", "السيارات", "التأشيرات", "عقود الإيجار", "الاشتراكات العامة", "الأقساط"]
    for sec in sections:
        st.markdown(f"<h5 style='color:#1B2559; font-family:Cairo; font-weight:800; margin-top:15px;'>{sec}</h5>", unsafe_allow_html=True)
        current_warn = sys_settings.get(sec, {}).get("warning_days", 30)
        current_danger = sys_settings.get(sec, {}).get("danger_days", 0)
        c1, c2, c3 = st.columns([1, 1, 2])
        with c1: warn = st.number_input(f"أيام التحذير (أصفر 🟡) - {sec}", value=current_warn, key=f"w_{sec}")
        with c2: danger = st.number_input(f"أيام الحرج (أحمر 🔴) - {sec}", value=current_danger, key=f"d_{sec}")
        with c3:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button(f"💾 حفظ الإعدادات لـ {sec}", key=f"btn_{sec}"):
                requests.put(f"{API_URL}/settings/{sec}", json={"owner_id": UID, "warning_days": warn, "danger_days": danger})
                st.success("تم الحفظ بنجاح!"); time.sleep(1); st.rerun()
        st.markdown("<hr style='border:1px solid #E9EDF7;'>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

elif main_menu in ["بيانات المدير", "بيانات العمال", "جداول إضافية"]:
    icon_n = "💼" if main_menu == "بيانات المدير" else "👷" if main_menu == "بيانات العمال" else "📋"
    db_endpoint = "manager_pages" if main_menu == "بيانات المدير" else "custom_pages" if main_menu == "بيانات العمال" else "extra_pages"
    rec_endpoint = "manager_records" if main_menu == "بيانات المدير" else "custom_records" if main_menu == "بيانات العمال" else "extra_records"
    
    render_top_navbar(f"{main_menu} {icon_n}", "إدارة الجداول المخصصة بشكل حر")
    pages_data = fetch_data(f"{db_endpoint}/{UID}")
    
    st.markdown("<div class='erp-card' style='padding: 15px 20px;'>", unsafe_allow_html=True)
    if st.button("➕ إنشاء زر وجدول جديد", type="primary", key=f"btn_add_{db_endpoint}"): st.session_state[f"show_add_{db_endpoint}"] = not st.session_state.get(f"show_add_{db_endpoint}", False)
        
    if st.session_state.get(f"show_add_{db_endpoint}", False):
        st.markdown("<div style='margin-top:15px; padding:20px; border-radius:12px; background:#F4F7FE; border:1px solid #E9EDF7;'>", unsafe_allow_html=True)
        c_title, c_cols = st.columns(2)
        with c_title: page_title = st.text_input("اسم الزر", key=f"new_title_{db_endpoint}")
        with c_cols: page_columns = st.text_input("رؤوس الأعمدة (مفصولة بفاصلة)", key=f"new_cols_{db_endpoint}")
        if st.button("💾 حفظ وإنشاء الجدول", type="primary", key=f"save_{db_endpoint}"):
            if page_title and page_columns:
                cols_list = [c.strip() for c in page_columns.replace('،', ',').split(',') if c.strip()]
                requests.post(f"{API_URL}/{db_endpoint}/", json={"owner_id": UID, "title": page_title, "columns_data": json.dumps(cols_list)})
                st.session_state[f"show_add_{db_endpoint}"] = False; st.rerun()
            else: st.warning("الرجاء تعبئة جميع الحقول.")
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if pages_data:
        st.markdown("<h4 style='color:#64748B; margin-top:10px; margin-bottom:15px; font-family:Cairo; font-weight:800;'>الوصول السريع للجداول:</h4>", unsafe_allow_html=True)
        cols = st.columns(min(len(pages_data), 5))
        for i, page in enumerate(pages_data):
            col_idx = i % 5
            if i > 0 and col_idx == 0: cols = st.columns(5)
            with cols[col_idx]:
                is_active = st.session_state.get(f"active_{db_endpoint}") == page["id"]
                btn_type = "primary" if is_active else "secondary"
                if st.button(f"📁 {page['title']}", key=f"btn_{db_endpoint}_{page['id']}", use_container_width=True, type=btn_type):
                    st.session_state[f"active_{db_endpoint}"] = page["id"]; st.rerun()
                    
        active_page_id = st.session_state.get(f"active_{db_endpoint}")
        if active_page_id:
            active_page = next((p for p in pages_data if p["id"] == active_page_id), None)
            if active_page:
                st.markdown("<hr style='border:1px solid #E9EDF7; margin: 25px 0;'>", unsafe_allow_html=True)
                st.markdown(f"<h3 style='color:#1B2559; font-family:Cairo; font-weight:800; margin-bottom:20px; text-align:right;'>جدول: {active_page['title']}</h3>", unsafe_allow_html=True)
                
                try: columns_list = json.loads(active_page['columns_data'])
                except: columns_list = ["الاسم"]
                
                all_records = fetch_data(f"{rec_endpoint}/{UID}")
                page_records = [r for r in all_records if r.get("page_id") == active_page_id]
                parsed_records = []
                for pr in page_records:
                    try: data_dict = json.loads(pr['record_data']); parsed_records.append(data_dict)
                    except: pass
                    
                df_dynamic = pd.DataFrame(parsed_records)
                for col in columns_list:
                    if col not in df_dynamic.columns: df_dynamic[col] = ""
                if not df_dynamic.empty: df_dynamic = df_dynamic[columns_list]
                else: df_dynamic = pd.DataFrame(columns=columns_list)
                
                if not df_dynamic.empty:
                    html_table = "<div class='modern-table-wrapper' style='margin-bottom: 20px;'><table class='modern-table'><thead><tr>"
                    for h in columns_list: html_table += f"<th>{h}</th>"
                    html_table += "</tr></thead><tbody>"
                    for _, row in df_dynamic.iterrows():
                        html_table += "<tr>"
                        for col in columns_list: html_table += f"<td>{display_clean(row[col])}</td>"
                        html_table += "</tr>"
                    html_table += "</tbody></table></div>"
                    st.markdown(html_table, unsafe_allow_html=True)
                else: st.info("الجدول فارغ حالياً.")

                st.markdown("<h4 style='color:#1E293B; font-weight:800; margin-top:30px; margin-bottom:15px;'>أداة التحرير (أضف/عدل هنا):</h4>", unsafe_allow_html=True)
                display_columns = columns_list[::-1]
                df_to_edit = df_dynamic[display_columns]
                
                edited_dynamic_df = st.data_editor(df_to_edit, num_rows="dynamic", use_container_width=True, hide_index=True, key=f"dyn_edit_{active_page_id}")
                
                c_del, c_pdf, c_exp, c_save = st.columns([1, 1.5, 1.5, 2])
                with c_save:
                    if st.button("💾 حفظ الجدول بالكامل", type="primary", use_container_width=True, key=f"save_dyn_{active_page_id}"):
                        clean_df = edited_dynamic_df.replace({np.nan: "", None: ""}).astype(str)
                        save_data = clean_df.to_dict(orient="records")
                        requests.post(f"{API_URL}/{db_endpoint}/{active_page_id}/sync", json={"owner_id": UID, "records": save_data})
                        st.success("تم الحفظ بنجاح!"); time.sleep(0.5); st.rerun()
                with c_exp:
                    clean_export_df = edited_dynamic_df.replace({np.nan: "", None: ""}).astype(str)
                    st.download_button("📊 تصدير Excel", to_excel(clean_export_df[columns_list], active_page['title']), f"{active_page['title']}.xlsx", use_container_width=True, key=f"exp_{active_page_id}")
                with c_pdf:
                    clean_export_df = edited_dynamic_df.replace({np.nan: "", None: ""}).astype(str)
                    st.download_button("🖨️ طباعة PDF", to_pdf_html_basic(clean_export_df[columns_list], active_page['title']), f"{active_page['title']}.html", mime="text/html", use_container_width=True, key=f"pdf_{active_page_id}")
                with c_del:
                    if st.button("🗑️ حذف الزر والجدول", key=f"del_{active_page_id}"):
                        requests.delete(f"{API_URL}/{db_endpoint}/{active_page_id}/{UID}")
                        st.session_state[f"active_{db_endpoint}"] = None; st.rerun()

elif main_menu == "إدارة الأقساط":
    render_top_navbar("إدارة الأقساط 💰", "المتابعة المالية الذكية وجدولة الدفعات")
    endpoint = "installments"; selected_sub = "إدارة الأقساط"; raw_data = fetch_data(f"{endpoint}/{UID}")
    render_delete_notification(endpoint); manage_id = st.session_state.get("manage_installment_id", None)
    
    if manage_id:
        item = next((i for i in raw_data if i["id"] == manage_id), None)
        if item:
            if st.button("⬅ العودة للقائمة الرئيسية", type="primary"): st.session_state["manage_installment_id"] = None; st.rerun()
            st.markdown(f"<h3 style='color:#1E293B; font-weight:800; margin-top:15px; margin-bottom: 25px;'>📊 لوحة تحكم أقساط العميل: <span style='color:#4318FF;'>{item['client_name']}</span></h3>", unsafe_allow_html=True)
            try: payments = json.loads(item['payments_data'])
            except: payments = []
            
            df_pay = pd.DataFrame(payments)
            if not df_pay.empty:
                df_pay['amount_due'] = pd.to_numeric(df_pay['amount_due'], errors='coerce').fillna(0.0)
                df_pay['paid_amount'] = pd.to_numeric(df_pay['paid_amount'], errors='coerce').fillna(0.0)
                total_inst = df_pay['amount_due'].sum(); total_paid = item['advance_payment'] + df_pay['paid_amount'].sum()
                total_rem = (item['total_amount']) - total_paid; late_amt = 0.0; status_list = []; rem_inst_list = []
                
                for _, r in df_pay.iterrows():
                    a_due = round(float(r['amount_due']), 2); a_paid = round(float(r['paid_amount']), 2)
                    rem_inst = round(a_due - a_paid, 2); rem_inst_list.append(rem_inst)
                    if a_paid >= a_due: status_list.append("مكتمل")
                    elif pd.notnull(r['due_date']) and r['due_date'] != "":
                        if date.fromisoformat(r['due_date']) < date.today(): late_amt += rem_inst; status_list.append("متأخر")
                        else: status_list.append("قيد الانتظار")
                    else: status_list.append("غير محدد")
                        
                df_pay['المتبقي من القسط'] = rem_inst_list; df_pay['حالة القسط'] = status_list

                c4, c3, c2, c1 = st.columns(4) 
                with c1: st.markdown(f"<div class='summary-card'><h3>إجمالي مبلغ التقسيط</h3><h2>{total_inst:,.2f}</h2></div>", unsafe_allow_html=True)
                with c2: st.markdown(f"<div class='summary-card'><h3>إجمالي المبلغ المسدد</h3><h2>{total_paid:,.2f}</h2></div>", unsafe_allow_html=True)
                with c3: st.markdown(f"<div class='summary-card'><h3>إجمالي المبالغ المتبقية</h3><h2>{total_rem:,.2f}</h2></div>", unsafe_allow_html=True)
                with c4: st.markdown(f"<div class='summary-card danger'><h3 style='color:#EE5D50;'>إجمالي المبالغ المتأخرة</h3><h2>{late_amt:,.2f}</h2></div>", unsafe_allow_html=True)
                
                st.markdown("<h4 style='color:#1E293B; font-weight:800; text-align:right; margin-top:20px; margin-bottom:15px;'>الجدول التفصيلي للأقساط (قم بالتعديل أدناه واضغط حفظ)</h4>", unsafe_allow_html=True)
                df_edit = df_pay.copy().rename(columns={"installment_number": "القسط (م)", "amount_due": "مبلغ القسط", "due_date": "تاريخ القسط", "paid_amount": "المبلغ المدفوع", "payment_date": "تاريخ الدفع", "notes": "ملاحظات"})
                cols_order = ["القسط (م)", "تاريخ القسط", "مبلغ القسط", "المبلغ المدفوع", "تاريخ الدفع", "المتبقي من القسط", "حالة القسط", "ملاحظات"]
                
                edited_df = st.data_editor(
                    df_edit[cols_order[::-1]],
                    column_config={"القسط (م)": st.column_config.NumberColumn(disabled=True), "مبلغ القسط": st.column_config.NumberColumn(disabled=True, format="%.2f"), "تاريخ القسط": st.column_config.TextColumn(disabled=True), "المتبقي من القسط": st.column_config.NumberColumn(disabled=True, format="%.2f"), "حالة القسط": st.column_config.TextColumn(disabled=True), "المبلغ المدفوع": st.column_config.NumberColumn(required=True, default=0.0, format="%.2f")},
                    hide_index=True, use_container_width=True, key=f"editor_inst_data_{manage_id}" 
                )
                c_exp, c_save = st.columns([4, 1])
                with c_save:
                    if st.button("💾 حفظ التحديثات", type="primary", use_container_width=True):
                        updated_payments = []
                        for idx, row in edited_df.iterrows(): updated_payments.append({"installment_number": row["القسط (م)"], "due_date": row["تاريخ القسط"], "amount_due": float(row["مبلغ القسط"]), "paid_amount": float(row["المبلغ المدفوع"]), "payment_date": str(row["تاريخ الدفع"]) if pd.notnull(row["تاريخ الدفع"]) else "", "notes": str(row["ملاحظات"]) if pd.notnull(row["ملاحظات"]) else ""})
                        requests.put(f"{API_URL}/{endpoint}/{manage_id}", json={"owner_id": UID, "payments_data": json.dumps(updated_payments)})
                        st.success("تم التحديث بنجاح"); time.sleep(0.5); st.rerun()
                with c_exp: st.download_button("🖨️ طباعة جدول الأقساط PDF", to_pdf_html_with_dashboard(edited_df[cols_order], f"تقرير أقساط العميل: {item['client_name']}", total_inst, total_paid, total_rem, late_amt), f"installments_{manage_id}.html", mime="text/html")
    else:
        g_total = g_paid = g_rem = g_late = 0.0
        if raw_data:
            for plan in raw_data:
                g_total += plan.get('total_amount', 0.0); g_paid += plan.get('advance_payment', 0.0)
                try: p_data = json.loads(plan['payments_data'])
                except: p_data = []
                for p in p_data:
                    a_d = float(p.get("amount_due", 0)); a_p = float(p.get("paid_amount", 0))
                    g_paid += a_p
                    if a_p < a_d and p.get("due_date") and date.fromisoformat(p.get("due_date")) < date.today(): g_late += (a_d - a_p)
            g_rem = g_total - g_paid
            
        st.markdown(f"""
        <div style="display: flex; gap: 15px; margin-bottom: 25px; direction: rtl;">
            <div class="global-summary" style="flex:1;"><h4>إجمالي مبالغ العقود</h4><h2>{g_total:,.2f}</h2></div>
            <div class="global-summary" style="flex:1; border-color:#0284C7;"><h4>إجمالي المدفوعات للشركة</h4><h2 style="color:#0284C7;">{g_paid:,.2f}</h2></div>
            <div class="global-summary" style="flex:1; border-color:#D97706;"><h4>الديون المتبقية للشركة</h4><h2 style="color:#D97706;">{g_rem:,.2f}</h2></div>
            <div class="global-summary" style="flex:1; border-color:#EE5D50;"><h4>المتأخرات</h4><h2 style="color:#EE5D50;">{g_late:,.2f}</h2></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div class='erp-card' style='padding: 15px 20px;'>", unsafe_allow_html=True)
        col_search, col3, col2, col1 = st.columns([3, 1.2, 1, 1.5])
        with col1:
            if st.button("➕ إضافة عقد قسط جديد", type="primary", use_container_width=True): st.session_state[f"show_add_{endpoint}"] = not st.session_state.get(f"show_add_{endpoint}", False)
        with col2:
            if raw_data: st.download_button("📊 تصدير Excel", to_excel(prepare_export_df(pd.DataFrame(raw_data), selected_sub), selected_sub), f"{selected_sub}.xlsx", use_container_width=True)
        with col3:
            if raw_data: st.download_button("🖨️ تصدير PDF", to_pdf_html_with_dashboard(prepare_export_df(pd.DataFrame(raw_data), selected_sub), "تقرير كافة الأقساط"), f"{selected_sub}_تقرير.html", mime="text/html", use_container_width=True)
        with col_search: search_q = st.text_input("🔍", placeholder="بحث في العقود...", label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)

        if st.session_state.get(f"show_add_{endpoint}", False):
            st.markdown("<div class='erp-card' style='border-top: 4px solid #2563EB;'>", unsafe_allow_html=True)
            st.markdown(f"<h4 style='color:#1B2559; margin-bottom:20px; font-weight:800;'>📝 إضافة عقد قسط جديد</h4>", unsafe_allow_html=True)
            c3, c2, c1 = st.columns(3)
            with c1: client_name = st.text_input("اسم العميل"); title = st.text_input("العنوان (الوصف)")
            with c2: total_amount = st.number_input("المبلغ الإجمالي", min_value=0.0, value=0.0, step=100.0); advance_payment = st.number_input("المدفوع مقدم", min_value=0.0, value=0.0, step=100.0)
            with c3: installments_count = st.number_input("عدد الأقساط", min_value=1, value=12); period_months = st.number_input("مدة القسط بالشهور (تكرار)", min_value=1, value=1)
            first_date = custom_date_picker("تاريخ القسط الأول", key_suffix="add_inst_first")
            remaining = total_amount - advance_payment
            inst_value = remaining / installments_count if installments_count > 0 else 0
            st.info(f"💡 سيتم إنشاء {installments_count} أقساط، قيمة القسط الواحد: {inst_value:,.2f} ريال. (المتبقي: {remaining:,.2f} ريال)")
            if st.button("إنشاء جدول الأقساط والحفظ", type="primary"):
                if client_name and total_amount > 0 and first_date:
                    payments = []
                    for i in range(installments_count):
                        due_d = add_months(first_date, i * period_months)
                        payments.append({"installment_number": i + 1, "due_date": due_d.isoformat(), "amount_due": inst_value, "paid_amount": 0.0, "payment_date": "", "notes": ""})
                    requests.post(f"{API_URL}/{endpoint}/", json={"owner_id": UID, "client_name": client_name, "title": title, "total_amount": total_amount, "advance_payment": advance_payment, "installments_count": installments_count, "period_months": period_months, "first_installment_date": str(first_date), "payments_data": json.dumps(payments), "notes": ""})
                    st.session_state[f"show_add_{endpoint}"] = False; st.rerun()
                else: st.warning("تأكد من إدخال اسم العميل، المبلغ الإجمالي، وتاريخ القسط الأول.")
            st.markdown("</div>", unsafe_allow_html=True)
        
        if raw_data:
            df = pd.DataFrame(raw_data)
            if search_q: df = df[df.apply(lambda row: row.astype(str).str.contains(search_q, case=False).any(), axis=1)]
            if not df.empty:
                html_table = "<div class='modern-table-wrapper'><table class='modern-table'><thead><tr>"
                headers = ["م", "اسم العميل", "العنوان", "المبلغ الإجمالي", "المدفوع مقدم", "عدد الأقساط", "القسط القادم", "الإجراءات"]
                for h in headers: html_table += f"<th>{h}</th>"
                html_table += "</tr></thead><tbody>"
                for _, row in df.iterrows():
                    try: p_data = json.loads(row['payments_data'])
                    except: p_data = []
                    next_due = "<div class='status-badge status-success'>مكتمل</div>"
                    for p in p_data:
                        a_due = round(float(p.get("amount_due", 0)), 2)
                        a_paid = round(float(p.get("paid_amount", 0)), 2)
                        if a_paid < a_due and p.get("due_date"):
                            d_val = p.get("due_date")
                            days = (date.fromisoformat(d_val) - date.today()).days
                            if days < 0: next_due = f"<div class='status-badge status-danger'>متأخر<br>({d_val})</div>"
                            elif days <= 30: next_due = f"<div class='status-badge status-warning'>قريب<br>({d_val})</div>"
                            else: next_due = f"<div class='status-badge status-none'>{d_val}</div>"
                            break
                    html_table += f"<tr><td>{row['id']}</td><td><b>{display_clean(row.get('client_name'))}</b></td><td>{display_clean(row.get('title'))}</td><td>{row.get('total_amount'):,.2f}</td><td>{row.get('advance_payment'):,.2f}</td><td>{row.get('installments_count')}</td><td>{next_due}</td><td><span style='color:#A3AED0; font-size:12px; font-weight:700;'>إدارة بالأسفل</span></td></tr>"
                html_table += "</tbody></table></div>"
                st.markdown(html_table, unsafe_allow_html=True)
                
                st.markdown("<h4 style='color:#1E293B; font-weight:800; margin-top:25px; margin-bottom:15px; text-align:right;'>إدارة العقود السريعة</h4>", unsafe_allow_html=True)
                for _, row in df.iterrows():
                    with st.container():
                        c_del, c_manage, c_name = st.columns([1, 1, 4])
                        with c_name: st.markdown(f"<div style='padding:10px 15px; background:#FFFFFF; border-radius:8px; border:1px solid #E9EDF7; text-align:right; font-weight:700; color:#1E293B;'>عقد م: <b>{row['id']}</b> | {display_clean(row.get('client_name'))}</div>", unsafe_allow_html=True)
                        with c_manage:
                            if st.button("📊 إدارة الأقساط", key=f"manage_inst_{row['id']}", use_container_width=True): st.session_state["manage_installment_id"] = row['id']; st.rerun()
                        with c_del:
                            if st.button("🗑️ حذف", key=f"del_inst_{row['id']}", use_container_width=True): st.session_state['pending_delete'] = {'endpoint': endpoint, 'id': row['id'], 'time': time.time()}; st.rerun()
            else: st.info("لا توجد نتائج للبحث.")
        else: st.info("لم يتم تسجيل عقود أقساط.")

elif main_menu == "المتابعة الشاملة" and selected_sub:
    render_top_navbar(f"إدارة {selected_sub}", "إضافة، تعديل، وإدارة السجلات بسهولة")
    endpoint = ""
    if selected_sub == "الموظفين": endpoint = "employees"
    elif selected_sub == "السيارات": endpoint = "vehicles"
    elif selected_sub == "التأشيرات": endpoint = "visas"
    elif selected_sub == "عقود الإيجار": endpoint = "rents"
    elif selected_sub == "الاشتراكات العامة": endpoint = "subscriptions"
    
    render_delete_notification(endpoint)
    df = pd.DataFrame()
    raw_data = fetch_data(f"{endpoint}/{UID}")
    if raw_data:
        df = pd.DataFrame(raw_data)
        for col in df.columns:
            if 'expiry' in col or 'date' in col: df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d')

    st.markdown("<div class='erp-card' style='padding: 15px 20px;'>", unsafe_allow_html=True)
    col_search, col3, col2, col1 = st.columns([3, 1.2, 1, 1.5])
    with col1:
        if st.button("➕ إضافة سجل جديد", type="primary", use_container_width=True): st.session_state[f"show_add_{endpoint}"] = not st.session_state.get(f"show_add_{endpoint}", False); st.session_state[f"edit_id_{endpoint}"] = None
    with col2:
        if not df.empty: st.download_button("📊 تصدير Excel", to_excel(prepare_export_df(df, selected_sub), selected_sub), f"{selected_sub}.xlsx", use_container_width=True)
    with col3:
        if not df.empty: st.download_button("🖨 تصدير PDF", to_pdf_html_basic(prepare_export_df(df, selected_sub), f"تقرير - {selected_sub}"), f"{selected_sub}_تقرير.html", mime="text/html", use_container_width=True)
    with col_search: search_q = st.text_input("🔍", placeholder="بحث في السجلات...", label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.get(f"show_add_{endpoint}", False):
        st.markdown("<div class='erp-card' style='border-top: 4px solid #2563EB;'>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='color:#1B2559; margin-bottom:20px; font-weight:800;'>📝 إضافة سجل جديد لـ {selected_sub}</h4>", unsafe_allow_html=True)
        
        if selected_sub == "الموظفين":
            c2, c1 = st.columns(2)
            with c1: name = st.text_input("اسم الموظف", key="add_emp_name"); iq_num = st.text_input("رقم الإقامة", key="add_emp_iq_num"); sponsorship = st.text_input("الكفالة", key="add_emp_spon")
            with c2: iq_exp = custom_date_picker("تاريخ انتهاء الإقامة", key_suffix="add_iq"); ins_exp = custom_date_picker("تاريخ انتهاء التأمين", key_suffix="add_ins"); pass_exp = custom_date_picker("تاريخ انتهاء الجواز", key_suffix="add_pass")
            if st.button("حفظ السجل", type="primary", key="btn_add_emp"):
                requests.post(f"{API_URL}/{endpoint}/", json={"owner_id": UID, "name": name, "iqama_number": iq_num, "sponsorship": sponsorship, "iqama_expiry": str(iq_exp) if iq_exp else None, "health_insurance_expiry": str(ins_exp) if ins_exp else None, "passport_expiry": str(pass_exp) if pass_exp else None})
                st.session_state[f"show_add_{endpoint}"] = False; st.rerun()
        elif selected_sub == "السيارات":
            c2, c1 = st.columns(2)
            with c1: car_name = st.text_input("اسم السيارة", key="add_veh_name"); plate = st.text_input("رقم اللوحة", key="add_veh_plate"); reg_num = st.text_input("رقم الاستمارة", key="add_veh_reg")
            with c2: reg_exp = custom_date_picker("تاريخ انتهاء الاستمارة", key_suffix="add_reg_exp"); ins_exp = custom_date_picker("تاريخ انتهاء التأمين", key_suffix="add_ins_exp")
            if st.button("حفظ السجل", type="primary", key="btn_add_veh"):
                requests.post(f"{API_URL}/{endpoint}/", json={"owner_id": UID, "car_name": car_name, "plate_number": plate, "registration_number": reg_num, "registration_expiry": str(reg_exp) if reg_exp else None, "insurance_expiry": str(ins_exp) if ins_exp else None})
                st.session_state[f"show_add_{endpoint}"] = False; st.rerun()
        elif selected_sub == "التأشيرات":
            c2, c1 = st.columns(2)
            with c1: emp = st.text_input("الاسم", key="add_visa_emp"); visa_num = st.text_input("رقم التأشيرة", key="add_visa_num"); travel_d = custom_date_picker("تاريخ السفر", key_suffix="add_visa_trav")
            with c2: v_dur_m = st.text_input("مدة التأشيرة بالاشهر", value="0", key="add_visa_m"); v_dur_d = st.text_input("مدة التأشيرة بالايام", value="0", key="add_visa_d"); ext_count = st.number_input("عدد مرات التمديد", min_value=0, value=0, key="add_visa_ext")
            exp_date = calculate_visa_expiry(travel_d, v_dur_m, v_dur_d, ext_count)
            notes = st.text_area("ملاحظات", key="add_visa_notes")
            if st.button("حفظ السجل", type="primary", key="btn_add_visa"):
                requests.post(f"{API_URL}/{endpoint}/", json={"owner_id": UID, "employee_name": emp, "visa_number": visa_num, "visa_duration_months": str(v_dur_m), "visa_duration_days": str(v_dur_d), "extension_count": ext_count, "notes": notes, "travel_date": str(travel_d) if travel_d else None, "expiry_date": str(exp_date) if exp_date else None})
                st.session_state[f"show_add_{endpoint}"] = False; st.rerun()
        elif selected_sub == "عقود الإيجار":
            c3, c2, c1 = st.columns(3)
            with c1: tenant = st.text_input("اسم المستاجر", key="add_rent_ten"); apt_num = st.text_input("رقم الشقة", key="add_rent_apt"); contract_num = st.text_input("رقم العقد", key="add_rent_cont"); duration = st.text_input("مدة العقد", key="add_rent_dur")
            with c2: start_d = custom_date_picker("تاريخ بداية العقد", key_suffix="add_rent_start"); exp = custom_date_picker("تاريخ انتهاء العقد", key_suffix="add_rent_exp"); next_pay = custom_date_picker("تاريخ الدفعة القادمة", key_suffix="add_rent_next")
            with c3: pay_amt = st.text_input("مبلغ الدفعة", key="add_rent_amt"); period_m = st.text_input("فترة الدفع بالشهر", key="add_rent_per"); ann_rent = st.text_input("مبلغ الايجار السنوي", key="add_rent_ann")
            if st.button("حفظ السجل", type="primary", key="btn_add_rent"):
                requests.post(f"{API_URL}/{endpoint}/", json={"owner_id": UID, "tenant_name": tenant, "apartment_number": apt_num, "contract_number": contract_num, "contract_duration": duration, "payment_amount": pay_amt, "payment_period_months": period_m, "annual_rent": ann_rent, "contract_start_date": str(start_d) if start_d else None, "contract_expiry": str(exp) if exp else None, "next_payment_date": str(next_pay) if next_pay else None})
                st.session_state[f"show_add_{endpoint}"] = False; st.rerun()
        elif selected_sub == "الاشتراكات العامة":
            c2, c1 = st.columns(2)
            with c1: srv = st.text_input("اسم الاشتراك او الترخيص", key="add_sub_srv"); sub_num = st.text_input("الرقم", key="add_sub_num")
            with c2: exp = custom_date_picker("تاريخ الانتهاء", key_suffix="add_sub_exp")
            notes = st.text_area("ملاحظات", key="add_sub_notes")
            if st.button("حفظ السجل", type="primary", key="btn_add_sub"):
                requests.post(f"{API_URL}/{endpoint}/", json={"owner_id": UID, "service_name": srv, "subscription_number": sub_num, "notes": notes, "subscription_expiry": str(exp) if exp else None})
                st.session_state[f"show_add_{endpoint}"] = False; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    edit_id = st.session_state.get(f"edit_id_{endpoint}", None)
    if edit_id is not None:
        item_to_edit = next((item for item in raw_data if item["id"] == edit_id), None)
        if item_to_edit:
            st.markdown("<div class='erp-card' style='border-top: 4px solid #F59E0B;'>", unsafe_allow_html=True)
            st.markdown(f"<h4 style='color:#1E293B; margin-bottom:20px; font-family:Cairo;'>✏️ تعديل السجل رقم ({edit_id})</h4>", unsafe_allow_html=True)
            if selected_sub == "الموظفين":
                c2, c1 = st.columns(2)
                with c1: name = st.text_input("اسم الموظف", value=clean_none(item_to_edit.get("name")), key=f"edit_emp_n_{edit_id}"); iq_num = st.text_input("رقم الإقامة", value=clean_none(item_to_edit.get("iqama_number")), key=f"edit_emp_iq_{edit_id}"); sponsorship = st.text_input("الكفالة", value=clean_none(item_to_edit.get("sponsorship")), key=f"edit_emp_sp_{edit_id}")
                with c2: iq_exp = custom_date_picker("تاريخ انتهاء الإقامة", default_date=item_to_edit.get("iqama_expiry"), key_suffix=f"edit_iq_d_{edit_id}"); ins_exp = custom_date_picker("تاريخ انتهاء التأمين", default_date=item_to_edit.get("health_insurance_expiry"), key_suffix=f"edit_ins_d_{edit_id}"); pass_exp = custom_date_picker("تاريخ انتهاء الجواز", default_date=item_to_edit.get("passport_expiry"), key_suffix=f"edit_pass_d_{edit_id}")
                if st.button("حفظ التعديلات", type="primary", key=f"btn_save_emp_{edit_id}"):
                    requests.put(f"{API_URL}/{endpoint}/{edit_id}", json={"owner_id": UID, "name": name, "iqama_number": iq_num, "sponsorship": sponsorship, "iqama_expiry": str(iq_exp) if iq_exp else None, "health_insurance_expiry": str(ins_exp) if ins_exp else None, "passport_expiry": str(pass_exp) if pass_exp else None})
                    st.session_state[f"edit_id_{endpoint}"] = None; st.rerun()
            elif selected_sub == "السيارات":
                c2, c1 = st.columns(2)
                with c1: car_name = st.text_input("اسم السيارة", value=clean_none(item_to_edit.get("car_name")), key=f"edit_veh_n_{edit_id}"); plate = st.text_input("رقم اللوحة", value=clean_none(item_to_edit.get("plate_number")), key=f"edit_veh_p_{edit_id}"); reg_num = st.text_input("رقم الاستمارة", value=clean_none(item_to_edit.get("registration_number")), key=f"edit_veh_r_{edit_id}")
                with c2: reg_exp = custom_date_picker("تاريخ انتهاء الاستمارة", default_date=item_to_edit.get("registration_expiry"), key_suffix=f"edit_reg_d_{edit_id}"); ins_exp = custom_date_picker("تاريخ انتهاء التأمين", default_date=item_to_edit.get("insurance_expiry"), key_suffix=f"edit_ins_d_{edit_id}")
                if st.button("حفظ التعديلات", type="primary", key=f"btn_save_veh_{edit_id}"):
                    requests.put(f"{API_URL}/{endpoint}/{edit_id}", json={"owner_id": UID, "car_name": car_name, "plate_number": plate, "registration_number": reg_num, "registration_expiry": str(reg_exp) if reg_exp else None, "insurance_expiry": str(ins_exp) if ins_exp else None})
                    st.session_state[f"edit_id_{endpoint}"] = None; st.rerun()
            elif selected_sub == "التأشيرات":
                c2, c1 = st.columns(2)
                with c1: emp = st.text_input("الاسم", value=clean_none(item_to_edit.get("employee_name")), key=f"edit_visa_e_{edit_id}"); visa_num = st.text_input("رقم التأشيرة", value=clean_none(item_to_edit.get("visa_number")), key=f"edit_visa_n_{edit_id}"); travel_d = custom_date_picker("تاريخ السفر", default_date=item_to_edit.get("travel_date"), key_suffix=f"edit_trav_d_{edit_id}")
                with c2: v_dur_m = st.text_input("مدة التأشيرة بالاشهر", value=clean_none(item_to_edit.get("visa_duration_months")), key=f"edit_visa_m_{edit_id}"); v_dur_d = st.text_input("مدة التأشيرة بالايام", value=clean_none(item_to_edit.get("visa_duration_days")), key=f"edit_visa_d_{edit_id}"); ext_count = st.number_input("عدد مرات التمديد", min_value=0, value=int(item_to_edit.get("extension_count") or 0), key=f"edit_visa_ext_{edit_id}")
                exp_date = calculate_visa_expiry(travel_d, v_dur_m, v_dur_d, ext_count)
                notes = st.text_area("ملاحظات", value=clean_none(item_to_edit.get("notes")), key=f"edit_visa_notes_{edit_id}")
                if st.button("حفظ التعديلات", type="primary", key=f"btn_save_visa_{edit_id}"):
                    requests.put(f"{API_URL}/{endpoint}/{edit_id}", json={"owner_id": UID, "employee_name": emp, "visa_number": visa_num, "visa_duration_months": str(v_dur_m), "visa_duration_days": str(v_dur_d), "extension_count": ext_count, "notes": notes, "travel_date": str(travel_d) if travel_d else None, "expiry_date": str(exp_date) if exp_date else None})
                    st.session_state[f"edit_id_{endpoint}"] = None; st.rerun()
            elif selected_sub == "عقود الإيجار":
                c3, c2, c1 = st.columns(3)
                with c1: tenant = st.text_input("اسم المستاجر", value=clean_none(item_to_edit.get("tenant_name")), key=f"edit_rent_t_{edit_id}"); apt_num = st.text_input("رقم الشقة", value=clean_none(item_to_edit.get("apartment_number")), key=f"edit_rent_a_{edit_id}"); contract_num = st.text_input("رقم العقد", value=clean_none(item_to_edit.get("contract_number")), key=f"edit_rent_c_{edit_id}"); duration = st.text_input("مدة العقد", value=clean_none(item_to_edit.get("contract_duration")), key=f"edit_rent_dur_{edit_id}")
                with c2: start_d = custom_date_picker("تاريخ بداية العقد", default_date=item_to_edit.get("contract_start_date"), key_suffix=f"edit_rent_start_{edit_id}"); exp = custom_date_picker("تاريخ انتهاء العقد", default_date=item_to_edit.get("contract_expiry"), key_suffix=f"edit_rent_exp_{edit_id}"); next_pay = custom_date_picker("تاريخ الدفعة القادمة", default_date=item_to_edit.get("next_payment_date"), key_suffix=f"edit_rent_next_{edit_id}")
                with c3: pay_amt = st.text_input("مبلغ الدفعة", value=clean_none(item_to_edit.get("payment_amount")), key=f"edit_rent_amt_{edit_id}"); period_m = st.text_input("فترة الدفع بالشهر", value=clean_none(item_to_edit.get("payment_period_months")), key=f"edit_rent_per_{edit_id}"); ann_rent = st.text_input("مبلغ الايجار السنوي", value=clean_none(item_to_edit.get("annual_rent")), key=f"edit_rent_ann_{edit_id}")
                if st.button("حفظ التعديلات", type="primary", key=f"btn_save_rent_{edit_id}"):
                    requests.put(f"{API_URL}/{endpoint}/{edit_id}", json={"owner_id": UID, "tenant_name": tenant, "apartment_number": apt_num, "contract_number": contract_num, "contract_duration": duration, "payment_amount": pay_amt, "payment_period_months": period_m, "annual_rent": ann_rent, "contract_start_date": str(start_d) if start_d else None, "contract_expiry": str(exp) if exp else None, "next_payment_date": str(next_pay) if next_pay else None})
                    st.session_state[f"edit_id_{endpoint}"] = None; st.rerun()
            elif selected_sub == "الاشتراكات العامة":
                c2, c1 = st.columns(2)
                with c1: srv = st.text_input("اسم الاشتراك او الترخيص", value=clean_none(item_to_edit.get("service_name")), key=f"edit_sub_s_{edit_id}"); sub_num = st.text_input("الرقم", value=clean_none(item_to_edit.get("subscription_number")), key=f"edit_sub_n_{edit_id}")
                with c2: exp = custom_date_picker("تاريخ الانتهاء", default_date=item_to_edit.get("subscription_expiry"), key_suffix=f"edit_sub_exp_{edit_id}")
                notes = st.text_area("ملاحظات", value=clean_none(item_to_edit.get("notes")), key=f"edit_sub_notes_{edit_id}")
                if st.button("حفظ التعديلات", type="primary", key=f"btn_save_sub_{edit_id}"):
                    requests.put(f"{API_URL}/{endpoint}/{edit_id}", json={"owner_id": UID, "service_name": srv, "subscription_number": sub_num, "notes": notes, "subscription_expiry": str(exp) if exp else None})
                    st.session_state[f"edit_id_{endpoint}"] = None; st.rerun()
            if st.button("❌ إلغاء التعديل", key=f"btn_cancel_{edit_id}"): st.session_state[f"edit_id_{endpoint}"] = None; st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    if not df.empty:
        if search_q: df = df[df.apply(lambda row: row.astype(str).str.contains(search_q, case=False).any(), axis=1)]
        if selected_sub == "الموظفين":
            html_table = "<div class='modern-table-wrapper'><table class='modern-table'><thead><tr>"
            headers = ["م", "اسم الموظف", "رقم الإقامة", "تاريخ الانتهاء", "ايام متبقية", "انتهاء التأمين", "ايام متبقية", "الكفالة", "انتهاء الجواز", "ايام متبقية"]
            for h in headers: html_table += f"<th>{h}</th>"
            html_table += "</tr></thead><tbody>"
            for _, row in df.iterrows():
                html_table += f"<tr><td>{row['id']}</td><td><b>{display_clean(row.get('name'))}</b></td><td>{display_clean(row.get('iqama_number'))}</td><td>{display_clean(row.get('iqama_expiry'))}</td><td>{format_status(row.get('iqama_expiry'), 'الموظفين')}</td><td>{display_clean(row.get('health_insurance_expiry'))}</td><td>{format_status(row.get('health_insurance_expiry'), 'الموظفين')}</td><td>{display_clean(row.get('sponsorship'))}</td><td>{display_clean(row.get('passport_expiry'))}</td><td>{format_status(row.get('passport_expiry'), 'الموظفين')}</td></tr>"
            html_table += "</tbody></table></div>"
            st.markdown(html_table, unsafe_allow_html=True)
            st.markdown("<h4 style='color:#1E293B; margin-top:20px; font-weight:800; text-align:right;'>إدارة السجلات السريعة</h4>", unsafe_allow_html=True)
            for _, row in df.iterrows():
                with st.container():
                    c_del, c_edit, c_name = st.columns([1, 1, 4])
                    with c_name: st.markdown(f"<div style='padding:10px 15px; background:#FFFFFF; border-radius:8px; border:1px solid #E9EDF7; text-align:right; font-weight:700; color:#1E293B;'>سجل م: <b>{row['id']}</b> | {display_clean(row.get('name'))}</div>", unsafe_allow_html=True)
                    with c_edit:
                        if st.button("✏️ تعديل", key=f"e_{row['id']}", use_container_width=True): st.session_state[f"edit_id_{endpoint}"] = row['id']; st.rerun()
                    with c_del:
                        if st.button("🗑️ حذف", key=f"d_{row['id']}", use_container_width=True): st.session_state['pending_delete'] = {'endpoint': endpoint, 'id': row['id'], 'time': time.time()}; st.rerun()
        
        elif selected_sub == "السيارات":
            html_table = "<div class='modern-table-wrapper'><table class='modern-table'><thead><tr>"
            headers = ["م", "اسم السيارة", "رقم اللوحة", "رقم الاستمارة", "تاريخ انتهاء الاستمارة", "ايام متبقية", "تاريخ انتهاء التامين", "ايام متبقية"]
            for h in headers: html_table += f"<th>{h}</th>"
            html_table += "</tr></thead><tbody>"
            for _, row in df.iterrows():
                html_table += f"<tr><td>{row['id']}</td><td><b>{display_clean(row.get('car_name'))}</b></td><td>{display_clean(row.get('plate_number'))}</td><td>{display_clean(row.get('registration_number'))}</td><td>{display_clean(row.get('registration_expiry'))}</td><td>{format_status(row.get('registration_expiry'), 'السيارات')}</td><td>{display_clean(row.get('insurance_expiry'))}</td><td>{format_status(row.get('insurance_expiry'), 'السيارات')}</td></tr>"
            html_table += "</tbody></table></div>"
            st.markdown(html_table, unsafe_allow_html=True)
            st.markdown("<h4 style='color:#1E293B; margin-top:20px; font-weight:800; text-align:right;'>إدارة السجلات السريعة</h4>", unsafe_allow_html=True)
            for _, row in df.iterrows():
                with st.container():
                    c_del, c_edit, c_name = st.columns([1, 1, 4])
                    with c_name: st.markdown(f"<div style='padding:10px 15px; background:#FFFFFF; border-radius:8px; border:1px solid #E9EDF7; text-align:right; font-weight:700; color:#1E293B;'>سجل م: <b>{row['id']}</b> | {display_clean(row.get('car_name'))}</div>", unsafe_allow_html=True)
                    with c_edit:
                        if st.button("✏️️ تعديل", key=f"e_{row['id']}", use_container_width=True): st.session_state[f"edit_id_{endpoint}"] = row['id']; st.rerun()
                    with c_del:
                        if st.button("🗑️ حذف", key=f"d_{row['id']}", use_container_width=True): st.session_state['pending_delete'] = {'endpoint': endpoint, 'id': row['id'], 'time': time.time()}; st.rerun()

        elif selected_sub == "التأشيرات":
            html_table = "<div class='modern-table-wrapper'><table class='modern-table'><thead><tr>"
            headers = ["م", "الاسم", "رقم التاشيرة", "تاريخ السفر", "مدة (أشهر)", "مدة (أيام)", "تمديدات", "تاريخ الانتهاء", "ايام متبقية", "ملاحظات"]
            for h in headers: html_table += f"<th>{h}</th>"
            html_table += "</tr></thead><tbody>"
            for _, row in df.iterrows():
                html_table += f"<tr><td>{row['id']}</td><td><b>{display_clean(row.get('employee_name'))}</b></td><td>{display_clean(row.get('visa_number'))}</td><td>{display_clean(row.get('travel_date'))}</td><td>{display_clean(row.get('visa_duration_months'))}</td><td>{display_clean(row.get('visa_duration_days'))}</td><td>{display_clean(row.get('extension_count'))}</td><td>{display_clean(row.get('expiry_date'))}</td><td>{format_status(row.get('expiry_date'), 'التأشيرات')}</td><td>{display_clean(row.get('notes'))}</td></tr>"
            html_table += "</tbody></table></div>"
            st.markdown(html_table, unsafe_allow_html=True)
            st.markdown("<h4 style='color:#1E293B; margin-top:20px; font-weight:800; text-align:right;'>إدارة السجلات السريعة</h4>", unsafe_allow_html=True)
            for _, row in df.iterrows():
                with st.container():
                    c_del, c_edit, c_name = st.columns([1, 1, 4])
                    with c_name: st.markdown(f"<div style='padding:10px 15px; background:#FFFFFF; border-radius:8px; border:1px solid #E9EDF7; text-align:right; font-weight:700; color:#1E293B;'>سجل م: <b>{row['id']}</b> | {display_clean(row.get('employee_name'))}</div>", unsafe_allow_html=True)
                    with c_edit:
                        if st.button("✏️ تعديل", key=f"e_{row['id']}", use_container_width=True): st.session_state[f"edit_id_{endpoint}"] = row['id']; st.rerun()
                    with c_del:
                        if st.button("🗑️ حذف", key=f"d_{row['id']}", use_container_width=True): st.session_state['pending_delete'] = {'endpoint': endpoint, 'id': row['id'], 'time': time.time()}; st.rerun()

        elif selected_sub == "عقود الإيجار":
            html_table = "<div class='modern-table-wrapper'><table class='modern-table'><thead><tr>"
            headers = ["م", "المستاجر", "الشقة", "العقد", "بداية العقد", "المدة", "الانتهاء", "ايام متبقية", "الدفعة القادمة", "مبلغ", "فترة", "ايجار سنوي"]
            for h in headers: html_table += f"<th>{h}</th>"
            html_table += "</tr></thead><tbody>"
            for _, row in df.iterrows():
                html_table += f"<tr><td>{row['id']}</td><td><b>{display_clean(row.get('tenant_name'))}</b></td><td>{display_clean(row.get('apartment_number'))}</td><td>{display_clean(row.get('contract_number'))}</td><td>{display_clean(row.get('contract_start_date'))}</td><td>{display_clean(row.get('contract_duration'))}</td><td>{display_clean(row.get('contract_expiry'))}</td><td>{format_status(row.get('contract_expiry'), 'عقود الإيجار')}</td><td>{display_clean(row.get('next_payment_date'))}</td><td>{display_clean(row.get('payment_amount'))}</td><td>{display_clean(row.get('payment_period_months'))}</td><td>{display_clean(row.get('annual_rent'))}</td></tr>"
            html_table += "</tbody></table></div>"
            st.markdown(html_table, unsafe_allow_html=True)
            st.markdown("<h4 style='color:#1E293B; margin-top:20px; font-weight:800; text-align:right;'>إدارة السجلات السريعة</h4>", unsafe_allow_html=True)
            for _, row in df.iterrows():
                with st.container():
                    c_del, c_edit, c_name = st.columns([1, 1, 4])
                    with c_name: st.markdown(f"<div style='padding:10px 15px; background:#FFFFFF; border-radius:8px; border:1px solid #E9EDF7; text-align:right; font-weight:700; color:#1E293B;'>سجل م: <b>{row['id']}</b> | {display_clean(row.get('tenant_name'))}</div>", unsafe_allow_html=True)
                    with c_edit:
                        if st.button("✏️ تعديل", key=f"e_{row['id']}", use_container_width=True): st.session_state[f"edit_id_{endpoint}"] = row['id']; st.rerun()
                    with c_del:
                        if st.button("🗑️ حذف", key=f"d_{row['id']}", use_container_width=True): st.session_state['pending_delete'] = {'endpoint': endpoint, 'id': row['id'], 'time': time.time()}; st.rerun()

        elif selected_sub == "الاشتراكات العامة":
            html_table = "<div class='modern-table-wrapper'><table class='modern-table'><thead><tr>"
            headers = ["م", "اسم الاشتراك او الترخيص", "الرقم", "تاريخ الانتهاء", "ايام متبقية", "ملاحظات"]
            for h in headers: html_table += f"<th>{h}</th>"
            html_table += "</tr></thead><tbody>"
            for _, row in df.iterrows():
                html_table += f"<tr><td>{row['id']}</td><td><b>{display_clean(row.get('service_name'))}</b></td><td>{display_clean(row.get('subscription_number'))}</td><td>{display_clean(row.get('subscription_expiry'))}</td><td>{format_status(row.get('subscription_expiry'), 'الاشتراكات العامة')}</td><td>{display_clean(row.get('notes'))}</td></tr>"
            html_table += "</tbody></table></div>"
            st.markdown(html_table, unsafe_allow_html=True)
            st.markdown("<h4 style='color:#1E293B; margin-top:20px; font-weight:800; text-align:right;'>إدارة السجلات السريعة</h4>", unsafe_allow_html=True)
            for _, row in df.iterrows():
                with st.container():
                    c_del, c_edit, c_name = st.columns([1, 1, 4])
                    with c_name: st.markdown(f"<div style='padding:10px 15px; background:#FFFFFF; border-radius:8px; border:1px solid #E9EDF7; text-align:right; font-weight:700; color:#1E293B;'>سجل م: <b>{row['id']}</b> | {display_clean(row.get('service_name'))}</div>", unsafe_allow_html=True)
                    with c_edit:
                        if st.button("✏️ تعديل", key=f"e_{row['id']}", use_container_width=True): st.session_state[f"edit_id_{endpoint}"] = row['id']; st.rerun()
                    with c_del:
                        if st.button("🗑 حذف", key=f"d_{row['id']}", use_container_width=True): st.session_state['pending_delete'] = {'endpoint': endpoint, 'id': row['id'], 'time': time.time()}; st.rerun()