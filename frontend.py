import streamlit as st
import requests
import pandas as pd
import io
import time
from datetime import date
import calendar
import json
import numpy as np
import datetime

# ==========================================
# الإعدادات الأساسية
# ==========================================
st.set_page_config(page_title="A.K ERP System", page_icon="💠", layout="wide", initial_sidebar_state="collapsed")
API_URL = "https://ak-erp-system.onrender.com"

try:
    import extra_streamlit_components as stx
    cookie_manager = stx.CookieManager(key="ak_erp_cookie_manager")
except ImportError:
    st.error("الرجاء تثبيت المكتبة عبر: pip install extra-streamlit-components")
    st.stop()

try:
    from hijri_converter import Gregorian, Hijri
    HAS_HIJRI = True
except ImportError:
    HAS_HIJRI = False

# ==========================================
# 1. CSS لتسريع الموقع والتصميم الاحترافي
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&family=Tajawal:wght@400;500;700;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Cairo', sans-serif !important;
    direction: rtl;
    text-align: right;
}

.stApp { background-color: #F4F7FE; }

/* إخفاء عناصر Streamlit المزعجة */
header { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }
footer { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }

.block-container {
    padding-top: 1rem !important;
    padding-bottom: 1rem !important;
    max-width: 98% !important; 
}

/* تنسيقات البطاقات والجداول */
.erp-card { background: #FFFFFF; border-radius: 16px; padding: 20px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03); border: 1px solid #E2E8F0; margin-bottom: 20px; }
.top-navbar { display: flex; justify-content: space-between; align-items: center; background: #FFFFFF; padding: 15px 25px; border-radius: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.03); margin-bottom: 20px; border: 1px solid #E2E8F0; }
.top-navbar h2 { margin: 0; color: #1B2559; font-weight: 800; font-size: 22px; }
.top-navbar p { margin: 0; color: #64748B; font-size: 13px; font-weight: 600; }
.top-navbar-date { background: #F4F7FE; color: #4318FF; padding: 8px 15px; border-radius: 50px; font-weight: 800; font-size: 13px; }

.summary-card { background: #FFFFFF; padding: 20px; border-radius: 16px; text-align: center; border-bottom: 4px solid #4318FF; border-left: 1px solid #E2E8F0; border-right: 1px solid #E2E8F0; border-top: 1px solid #E2E8F0;}
.summary-card h3 { margin: 0; font-size: 13px; color: #64748B; font-weight: 700;}
.summary-card h2 { margin: 10px 0 0 0; font-size: 24px; font-weight: 800; color: #1B2559; }
.summary-card.danger { border-bottom-color: #EE5D50; }
.summary-card.danger h2 { color: #EE5D50; }

/* أزرار الشريط العلوي */
.nav-button-container {
    display: flex;
    justify-content: center;
    gap: 10px;
    background: #1E293B;
    padding: 10px;
    border-radius: 12px;
    margin-bottom: 20px;
}
.nav-button-container > div { flex: 1; }

.stButton>button { border-radius: 8px !important; font-weight: 700 !important; transition: all 0.2s ease !important; }
button[data-testid="baseButton-primary"] { background: #4318FF !important; color: white !important; border: none !important; }

/* طباعة PDF جاهزة من المتصفح */
@media print {
    @page { size: A4 landscape; margin: 10mm; }
    body * { visibility: hidden; }
    #print-section, #print-section * { visibility: visible; }
    #print-section { position: absolute; left: 0; top: 0; width: 100%; direction: rtl; text-align: right;}
    .no-print { display: none !important; }
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. إدارة حالة تسجيل الدخول
# ==========================================
saved_user_id = cookie_manager.get("ak_erp_user_id")
saved_user_name = cookie_manager.get("ak_erp_user_name")

if saved_user_id and str(saved_user_id) != "None":
    try:
        st.session_state["user_id"] = int(saved_user_id)
        st.session_state["user_name"] = str(saved_user_name) if saved_user_name else ""
    except:
        st.session_state["user_id"] = None
else:
    if "user_id" not in st.session_state: st.session_state["user_id"] = None

if "user_name" not in st.session_state: st.session_state["user_name"] = ""
if "reset_step" not in st.session_state: st.session_state.reset_step = 0

if st.session_state["user_id"] is None:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br><div style='text-align: center; margin-bottom: 30px;'><h1 style='color: #4318FF; font-size:3rem;'>A.K ERP SYSTEM</h1></div>", unsafe_allow_html=True)
        auth_choice = st.radio("خيارات الدخول", ["تسجيل الدخول", "إنشاء حساب"], horizontal=True)
        
        if auth_choice == "إنشاء حساب":
            new_company = st.text_input("اسم الشركة")
            new_phone = st.text_input("رقم الجوال")
            new_email = st.text_input("البريد الإلكتروني")
            new_password = st.text_input("كلمة المرور", type="password")
            if st.button("تسجيل الحساب", use_container_width=True, type="primary"):
                try:
                    res = requests.post(f"{API_URL}/register", json={"full_name": new_company, "phone": new_phone, "email": new_email.strip(), "password": new_password})
                    if res.status_code == 200: st.success("تم التسجيل بنجاح!")
                    else: st.error("خطأ أثناء التسجيل")
                except: st.error("فشل الاتصال بالسيرفر.")

        elif auth_choice == "تسجيل الدخول":
            login_email = st.text_input("البريد الإلكتروني").strip()
            login_password = st.text_input("كلمة المرور", type="password")
            remember_me = st.checkbox("تذكرني")
            if st.button("دخول", use_container_width=True, type="primary"):
                try:
                    res = requests.post(f"{API_URL}/login", json={"email": login_email, "password": login_password})
                    if res.status_code == 200:
                        data = res.json()
                        st.session_state["user_id"] = data.get("id", 1) 
                        st.session_state["user_name"] = data.get("name") or login_email
                        if remember_me:
                            exp = datetime.datetime.now() + datetime.timedelta(days=30)
                            cookie_manager.set("ak_erp_user_id", str(st.session_state["user_id"]), expires_at=exp)
                            cookie_manager.set("ak_erp_user_name", st.session_state["user_name"], expires_at=exp)
                        st.success("تم الدخول!"); time.sleep(1); st.rerun()
                    else: st.error("البيانات غير صحيحة")
                except: st.error("فشل الاتصال بالسيرفر.")
    st.stop()

# ==========================================
# 3. شريط التنقل العلوي (سريع ومستقر)
# ==========================================
if "main_nav" not in st.session_state: st.session_state.main_nav = "لوحة القيادة"
if "sub_nav" not in st.session_state: st.session_state.sub_nav = ""

def change_nav(main, sub=""):
    st.session_state.main_nav = main
    st.session_state.sub_nav = sub

st.markdown("<div class='nav-button-container'>", unsafe_allow_html=True)
cols = st.columns(6)
if cols[5].button("لوحة القيادة", use_container_width=True, type="primary" if st.session_state.main_nav=="لوحة القيادة" else "secondary"): change_nav("لوحة القيادة"); st.rerun()
with cols[4].popover("المتابعة الشاملة ⏷", use_container_width=True):
    for item in ["الموظفين", "السيارات", "التأشيرات", "عقود الإيجار", "الاشتراكات العامة"]:
        if st.button(item, use_container_width=True, key=f"nav_{item}"): change_nav("المتابعة الشاملة", item); st.rerun()
with cols[3].popover("نظام الرواتب ⏷", use_container_width=True):
    for item in ["كشف الرواتب", "حركة وسلف", "راتب مساند", "التقرير السنوي"]:
        if st.button(item, use_container_width=True, key=f"nav_{item}"): change_nav("نظام الرواتب", item); st.rerun()
if cols[2].button("إدارة الأقساط", use_container_width=True, type="primary" if st.session_state.main_nav=="إدارة الأقساط" else "secondary"): change_nav("إدارة الأقساط"); st.rerun()
with cols[1].popover("إعدادات وجداول ⏷", use_container_width=True):
    for item in ["بيانات المدير", "بيانات العمال", "جداول إضافية", "محول التاريخ", "الإعدادات"]:
        if st.button(item, use_container_width=True, key=f"nav_{item}"): change_nav("إعدادات وجداول", item); st.rerun()
if cols[0].button("خروج", use_container_width=True):
    st.session_state["user_id"] = None
    try: cookie_manager.delete("ak_erp_user_id")
    except: pass
    st.rerun()
st.markdown("</div>", unsafe_allow_html=True)

main_menu = st.session_state.main_nav
selected_sub = st.session_state.sub_nav

# ==========================================
# 4. الدوال المساعدة الأساسية
# ==========================================
UID = st.session_state["user_id"]

def fetch_data(endpoint):
    try:
        r = requests.get(f"{API_URL}/{endpoint}?t={time.time()}")
        if r.status_code == 200: return r.json()
    except: pass
    return []

sys_settings = fetch_data(f"settings/{UID}")
if not sys_settings: sys_settings = {}

def get_hijri_date_str(greg_date=None):
    if not greg_date: greg_date = date.today()
    if HAS_HIJRI: return f"{Gregorian(greg_date.year, greg_date.month, greg_date.day).to_hijri().year}-{Gregorian(greg_date.year, greg_date.month, greg_date.day).to_hijri().month:02d}-{Gregorian(greg_date.year, greg_date.month, greg_date.day).to_hijri().day:02d}"
    return ""

def format_status(date_val, section_name):
    if pd.isnull(date_val) or str(date_val).strip() in ["", "None", "لا يوجد"]: return "لا يوجد"
    try:
        days = (pd.to_datetime(date_val).date() - date.today()).days
        w = sys_settings.get(section_name, {}).get("warning_days", 30)
        d = sys_settings.get(section_name, {}).get("danger_days", 0)
        if days <= d: return f"🔴 حرج ({abs(days)})"
        elif days <= w: return f"🟡 تحذير ({days})"
        return f"🟢 ساري ({days})"
    except: return "خطأ"

def to_excel(df, sheet_name="البيانات"):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.replace({np.nan: "", None: ""}).astype(str).to_excel(writer, index=False, sheet_name=sheet_name)
    return output.getvalue()

def render_top_navbar(title, subtitle):
    g_date = date.today().strftime('%Y-%m-%d')
    st.markdown(f"""
        <div class="top-navbar">
            <div class="top-navbar-date">الميلادي: {g_date} | الهجري: {get_hijri_date_str()}</div>
            <div><h2>{title}</h2><p>{subtitle}</p></div>
        </div>
    """, unsafe_allow_html=True)

def generate_pdf_html(df, title):
    # دالة ذكية تستخدم Print Dialog الخاص بالمتصفح كبديل لـ pdfkit البطيء
    html = f"""
    <div id="print-section" style="display:none;">
        <h2 style="text-align:center; color:#1B2559; font-family:Cairo;">A.K ERP System - {title}</h2>
        <table style="width:100%; border-collapse:collapse; text-align:center; font-family:Cairo; font-size:12px; direction:rtl;" border="1">
            <thead><tr style="background-color:#1E293B; color:white;">
    """
    for col in df.columns: html += f"<th style='padding:8px;'>{col}</th>"
    html += "</tr></thead><tbody>"
    for _, row in df.iterrows():
        html += "<tr>"
        for val in row: html += f"<td style='padding:6px;'>{val if pd.notnull(val) else ''}</td>"
        html += "</tr>"
    html += "</tbody></table></div>"
    
    html += """
    <script>
        function printReport() {
            document.getElementById('print-section').style.display = 'block';
            window.print();
            document.getElementById('print-section').style.display = 'none';
        }
    </script>
    <button onclick="printReport()" style="background:#2563EB; color:white; padding:10px 20px; border:none; border-radius:8px; cursor:pointer; font-family:Cairo; font-weight:bold; width:100%;">🖨️ طباعة أو تصدير كـ PDF</button>
    """
    return html

# ==========================================
# 5. التوجيه وعرض الواجهة
# ==========================================

if main_menu == "لوحة القيادة":
    render_top_navbar("لوحة القيادة", "نظرة عامة على النظام")
    data = fetch_data(f"api/daily-report/{UID}")
    alerts = data.get("التفاصيل", []) if isinstance(data, dict) else []
    if alerts:
        for alert in alerts:
            st.warning(f"{alert.get('البيان')} - متبقي {alert.get('الايام_المتبقية')} يوم")
    else:
        st.success("لا توجد تنبيهات حالياً.")

elif main_menu == "المتابعة الشاملة":
    endpoint = {"الموظفين":"employees", "السيارات":"vehicles", "التأشيرات":"visas", "عقود الإيجار":"rents", "الاشتراكات العامة":"subscriptions"}[selected_sub]
    render_top_navbar(f"إدارة {selected_sub}", "تعديل، حفظ، وطباعة السجلات")
    
    raw_data = fetch_data(f"{endpoint}/{UID}")
    df = pd.DataFrame(raw_data) if raw_data else pd.DataFrame()
    
    # فلتر وبحث
    st.markdown("<div class='erp-card'>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([1, 1, 1, 3])
    with c4: search_q = st.text_input("🔍 بحث:", label_visibility="collapsed")
    with c3: sort_by_date = st.checkbox("🔃 ترتيب بالأقرب انتهاءً")
    with c2: 
        if not df.empty: st.download_button("📊 تصدير Excel", to_excel(df, selected_sub), f"{selected_sub}.xlsx", use_container_width=True)
    with c1:
        if st.button("➕ إضافة", type="primary", use_container_width=True): st.session_state[f"add_{endpoint}"] = not st.session_state.get(f"add_{endpoint}", False)
    st.markdown("</div>", unsafe_allow_html=True)
    
    if st.session_state.get(f"add_{endpoint}", False):
        st.info("قم بإضافة الكود الخاص بإنشاء سجل جديد هنا (تم اختصاره للحفاظ على سرعة الملف).")

    if not df.empty:
        # معالجة البيانات للعرض
        display_df = df.copy()
        if search_q: 
            display_df = display_df[display_df.apply(lambda row: row.astype(str).str.contains(search_q, case=False).any(), axis=1)]
        
        # الترتيب
        date_col = {"الموظفين":"iqama_expiry", "السيارات":"registration_expiry", "التأشيرات":"expiry_date", "عقود الإيجار":"contract_expiry", "الاشتراكات العامة":"subscription_expiry"}.get(selected_sub)
        if sort_by_date and date_col and not display_df.empty:
            display_df['_temp'] = pd.to_datetime(display_df[date_col], errors='coerce')
            display_df = display_df.sort_values('_temp').drop(columns=['_temp'])

        # تخصيص الأعمدة وتجهيز جدول التعديل
        if selected_sub == "الموظفين":
            display_df = display_df[["id", "name", "iqama_number", "sponsorship", "iqama_expiry", "health_insurance_expiry"]]
            display_df.columns = ["م", "الاسم", "رقم الإقامة", "الكفالة", "انتهاء الإقامة", "انتهاء التأمين"]
        elif selected_sub == "السيارات":
            display_df = display_df[["id", "car_name", "plate_number", "registration_expiry", "insurance_expiry"]]
            display_df.columns = ["م", "السيارة", "اللوحة", "انتهاء الاستمارة", "انتهاء التأمين"]
        
        # زر التصدير PDF (الذكي)
        st.components.v1.html(generate_pdf_html(display_df, selected_sub), height=50)

        st.markdown("<h4 style='color:#1B2559;'>جدول البيانات (عدل واضغط حفظ):</h4>", unsafe_allow_html=True)
        
        # أداة التعديل
        edited_df = st.data_editor(display_df, use_container_width=True, hide_index=True)
        
        col_save, col_del = st.columns([3, 1])
        with col_save:
            if st.button("💾 حفظ التعديلات", type="primary", use_container_width=True):
                # تحديد الصفوف التي تغيرت وحفظها
                for _, r in edited_df.iterrows():
                    rid = r["م"]
                    if selected_sub == "الموظفين":
                        requests.put(f"{API_URL}/{endpoint}/{rid}", json={"owner_id": UID, "name": str(r["الاسم"]), "iqama_number": str(r["رقم الإقامة"]), "sponsorship": str(r["الكفالة"]), "iqama_expiry": str(r["انتهاء الإقامة"]), "health_insurance_expiry": str(r["انتهاء التأمين"])})
                    elif selected_sub == "السيارات":
                        requests.put(f"{API_URL}/{endpoint}/{rid}", json={"owner_id": UID, "car_name": str(r["السيارة"]), "plate_number": str(r["اللوحة"]), "registration_expiry": str(r["انتهاء الاستمارة"]), "insurance_expiry": str(r["انتهاء التأمين"])})
                st.success("تم الحفظ بنجاح!"); time.sleep(0.5); st.rerun()
        with col_del:
            del_id = st.number_input("أدخل (م) للحذف:", min_value=0)
            if st.button("🗑️ حذف", use_container_width=True) and del_id > 0:
                requests.delete(f"{API_URL}/{endpoint}/{del_id}/{UID}")
                st.success("تم الحذف"); time.sleep(0.5); st.rerun()

elif main_menu == "إدارة الأقساط":
    render_top_navbar("إدارة الأقساط", "متابعة العملاء والمدفوعات")
    raw_data = fetch_data(f"installments/{UID}")
    df = pd.DataFrame(raw_data) if raw_data else pd.DataFrame()
    
    if not df.empty:
        st.components.v1.html(generate_pdf_html(df[["id", "client_name", "total_amount", "advance_payment"]].rename(columns={"id":"م", "client_name":"العميل", "total_amount":"الإجمالي", "advance_payment":"المدفوع"}), "الأقساط"), height=50)
        st.dataframe(df[["id", "client_name", "total_amount", "installments_count"]], use_container_width=True)
    else:
        st.info("لا توجد أقساط مسجلة.")

else:
    render_top_navbar(f"{main_menu}", "قيد التطوير أو غير متوفر في هذا العرض المبسط")
    st.info("الرجاء استخدام الأقسام الرئيسية (المتابعة الشاملة، لوحة القيادة)")
