import streamlit as st
import json
import os
import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import zipfile
import io
import base64

# הגדרת הקבצי JSON
DATA_DIR = "DATA"
DATA_FILE = os.path.join(DATA_DIR, "clients_data.json")
PRODUCTS_FILE = os.path.join(DATA_DIR, "products.json")
STATUS_FILE = os.path.join(DATA_DIR, "status.json")

# יצירת קבצי JSON אם אינם קיימים
def init_json_files():
    # יצירת ספריית DATA אם אינה קיימת
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    # יצירת קובץ נתוני לקוחות
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False)
    
    # יצירת קובץ סוגי מוצרים
    if not os.path.exists(PRODUCTS_FILE):
        with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
            default_products = {
                "סוגי מוצרים": [
                    "דלת עץ",
                    "דלת פלדה",
                    "חלון עץ",
                    "חלון אלומיניום",
                    "פרגולה",
                    "ריהוט גן",
                    "מטבח",
                    "ארון קיר"
                ]
            }
            json.dump(default_products, f, ensure_ascii=False, indent=4)
    
    # יצירת קובץ סטטוסי פעולה
    if not os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "w", encoding="utf-8") as f:
            default_status = {
                "סטטוסי פעולה": [
                    "יושם",
                    "בתהליך",
                    "תקוע"
                ]
            }
            json.dump(default_status, f, ensure_ascii=False, indent=4)

# טעינת הנתונים מקובץ JSON
def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

# טעינת סוגי המוצרים מקובץ JSON
def load_products():
    with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            default_products = {"סוגי מוצרים": []}
            return default_products

# טעינת סטטוסי פעולה מקובץ JSON
def load_status():
    with open(STATUS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            default_status = {"סטטוסי פעולה": []}
            return default_status

# שמירת הנתונים לקובץ JSON
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# שמירת סוגי המוצרים לקובץ JSON
def save_products(products_data):
    with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
        json.dump(products_data, f, ensure_ascii=False, indent=4)

# שמירת סטטוסי פעולה לקובץ JSON
def save_status(status_data):
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(status_data, f, ensure_ascii=False, indent=4)

# פונקציה להכנת נתונים לדשבורד הצעות מחיר
def prepare_proposals_dashboard_data(data):
    proposals_data = []
    
    for client_name, client_info in data.items():
        # מידע מהשלב של הצעת המחיר
        proposal_info = client_info.get("הצעת מחיר", {})
        proposal_status = proposal_info.get("האם יצאה הצעה?", "לא")
        proposal_amount = proposal_info.get("סכום הצעת מחיר", "0 ש\"ח")
        
        # מידע מהשלב של אישור הזמנה
        order_info = client_info.get("אישור הזמנה", {})
        
        # קביעת סטטוס הצעת המחיר
        if order_info:  # אם יש אישור הזמנה
            status = "מאושרת"
            status_color = "ירוק"
        elif proposal_status == "כן":  # אם יצאה הצעה אבל אין אישור
            status = "נשלחה"
            status_color = "כתום"
        else:  # אם אין הצעה בכלל
            status = "לא נשלחה"
            status_color = "אדום"
        
        # הוצאת סכום המספרי מהמחרוזת "X,XXX ש\"ח"
        try:
            amount_str = proposal_amount.split(" ")[0].replace(",", "")
            amount = int(amount_str) if amount_str.isdigit() else 0
        except (ValueError, IndexError):
            amount = 0
        
        proposals_data.append({
            "שם לקוח": client_name,
            "סטטוס": status,
            "צבע": status_color,
            "סכום": amount
        })
    
    return pd.DataFrame(proposals_data)

# יצירת קובץ ZIP עם כל קבצי ה-JSON להורדה
def create_zip_download_link():
    # יצירת קובץ ZIP בזיכרון
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        # הוספת קובץ הלקוחות
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                zip_file.writestr("clients_data.json", f.read())
                
        # הוספת קובץ המוצרים
        if os.path.exists(PRODUCTS_FILE):
            with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
                zip_file.writestr("products.json", f.read())
                
        # הוספת קובץ הסטטוסים
        if os.path.exists(STATUS_FILE):
            with open(STATUS_FILE, "r", encoding="utf-8") as f:
                zip_file.writestr("status.json", f.read())
    
    # הכנת הקובץ להורדה
    zip_buffer.seek(0)
    b64 = base64.b64encode(zip_buffer.read()).decode()
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # יצירת קישור להורדה
    href = f'<a href="data:application/zip;base64,{b64}" download="crm_data_{current_date}.zip" class="download-button">הורד קבצי מערכת כ-ZIP</a>'
    
    return href

# הגדרת פונקציה לפורמט תאריך ושעה
def format_datetime(date_str, time_str=None):
    if not date_str:
        return ""
    
    if time_str:
        return f"{date_str} {time_str}"
    return date_str

# הגדרת הממשק וההגיון של האפליקציה
def main():
    st.set_page_config(page_title="מערכת ניהול מתעניינים", layout="wide")
    
    # CSS לתמיכה בעברית וסגנון כללי וגם התאמה למכשירים ניידים
    st.markdown("""
    <style>
    body {
        direction: rtl;
        text-align: right;
    }
    .stButton button {
        width: 100%;
    }
    .stTextInput, .stSelectbox, .stDateInput, .stTimeInput {
        direction: rtl;
        text-align: right;
    }
    div[data-testid="stTable"] {
        direction: rtl;
    }
    .highlight {
        background-color: yellow;
    }
    /* עיצוב כפתור ההורדה */
    .download-button {
        display: inline-block;
        padding: 0.5rem 1rem;
        background-color: #4CAF50;
        color: white;
        text-align: center;
        text-decoration: none;
        font-size: 16px;
        border-radius: 4px;
        cursor: pointer;
        margin: 10px 0;
    }
    .download-button:hover {
        background-color: #45a049;
    }
    /* התאמה למכשירים ניידים */
    @media (max-width: 768px) {
        .stApp {
            padding: 0.5rem;
        }
        .stButton button {
            font-size: 0.8rem;
            padding: 0.3rem;
        }
        input, select, textarea {
            font-size: 16px !important; /* מניעת זום אוטומטי ב-iOS */
        }
        .stDateInput, .stTimeInput {
            max-width: 100%;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # כותרת ראשית
    st.title("מערכת ניהול מתעניינים")
    
    # יצירת קבצי JSON אם אינם קיימים
    init_json_files()
    
    # טעינת הנתונים
    data = load_data()
    products_data = load_products()
    status_data = load_status()
    
    # הכנת נתוני דשבורד
    df_proposals = prepare_proposals_dashboard_data(data)
    
    # יצירת תפריט צדדי
    menu = ["שיחת טלפון - מתעניין חדש", 
            "פגישה/דוגמאות", 
            "הצעת מחיר", 
            "אישור הזמנה", 
            "רכש ויבוא", 
            "בדיקת האתר", 
            "התקנה וגבייה",
            "מעקב ותזכורות"]
    
    # בחירת אפשרות ניהול וקישור לדשבורד הראשי
    manage_options = ["דשבורד ראשי", "ניהול סוגי מוצרים", "ניהול סטטוסי פעולה", "גיבוי נתונים"]
    manage_option = st.sidebar.radio("ניווט מהיר", manage_options, index=0)
    
    # קבלת פרמטרים מה-URL אם יש
    query_params = st.query_params
    if "page" in query_params:
        page = query_params["page"]
        if page == "new_client":
            choice = "שיחת טלפון - מתעניין חדש"
        elif page == "price_proposal":
            choice = "הצעת מחיר"
        elif page == "followup":
            choice = "מעקב ותזכורות"
        else:
            choice = st.sidebar.selectbox("בחר שלב", menu, index=0)
    else:
        choice = st.sidebar.selectbox("בחר שלב", menu, index=0)
    
    # טיפול בניווט מהיר לדשבורד
    if manage_option == "דשבורד ראשי":
        st.query_params.clear()
        choice = None  # מאפשר הצגת הדשבורד
    
    # רשימת לקוחות קיימים
    client_names = list(data.keys())
    
    # הצגת דשבורד בעמוד הראשי אם לא נבחר שלב או יש שינוי query params
    if manage_option == "ניהול סוגי מוצרים":
        # קוד ניהול סוגי מוצרים
        st.header("ניהול סוגי מוצרים")
        
        # הצגת רשימת סוגי המוצרים הקיימים
        st.subheader("סוגי מוצרים קיימים")
        
        product_types = products_data.get("סוגי מוצרים", [])
        
        if product_types:
            # הצגת טבלת מוצרים
            df = pd.DataFrame({"סוג מוצר": product_types})
            st.dataframe(df)
        else:
            st.info("אין סוגי מוצרים מוגדרים במערכת")
        
        # הוספת סוג מוצר חדש
        st.subheader("הוספת סוג מוצר חדש")
        
        with st.form("add_product_type_form"):
            new_product_type = st.text_input("שם סוג המוצר החדש")
            submit_button = st.form_submit_button("הוסף סוג מוצר")
            
            if submit_button and new_product_type:
                if new_product_type in product_types:
                    st.warning(f"סוג המוצר '{new_product_type}' כבר קיים במערכת")
                else:
                    products_data["סוגי מוצרים"].append(new_product_type)
                    save_products(products_data)
                    st.success(f"סוג המוצר '{new_product_type}' נוסף בהצלחה")
                    st.rerun()
        
        # מחיקת סוג מוצר
        st.subheader("מחיקת סוג מוצר")
        
        with st.form("delete_product_type_form"):
            if product_types:
                product_to_delete = st.selectbox("בחר סוג מוצר למחיקה", product_types)
                submit_button = st.form_submit_button("מחק סוג מוצר")
                
                if submit_button and product_to_delete:
                    products_data["סוגי מוצרים"].remove(product_to_delete)
                    save_products(products_data)
                    st.success(f"סוג המוצר '{product_to_delete}' נמחק בהצלחה")
                    st.rerun()
            else:
                st.info("אין סוגי מוצרים למחיקה")
                st.form_submit_button("מחק סוג מוצר", disabled=True)
    
    elif manage_option == "ניהול סטטוסי פעולה":
        st.header("ניהול סטטוסי פעולה")
        
        # הצגת רשימת סטטוסי הפעולה הקיימים
        st.subheader("סטטוסי פעולה קיימים")
        
        status_types = status_data.get("סטטוסי פעולה", [])
        
        if status_types:
            # הצגת טבלת סטטוסים
            df = pd.DataFrame({"סטטוס פעולה": status_types})
            st.dataframe(df)
        else:
            st.info("אין סטטוסי פעולה מוגדרים במערכת")
        
        # הוספת סטטוס פעולה חדש
        st.subheader("הוספת סטטוס פעולה חדש")
        
        with st.form("add_status_type_form"):
            new_status_type = st.text_input("שם סטטוס הפעולה החדש")
            submit_button = st.form_submit_button("הוסף סטטוס פעולה")
            
            if submit_button and new_status_type:
                if new_status_type in status_types:
                    st.warning(f"סטטוס הפעולה '{new_status_type}' כבר קיים במערכת")
                else:
                    status_data["סטטוסי פעולה"].append(new_status_type)
                    save_status(status_data)
                    st.success(f"סטטוס הפעולה '{new_status_type}' נוסף בהצלחה")
                    st.rerun()
        
        # מחיקת סטטוס פעולה
        st.subheader("מחיקת סטטוס פעולה")
        
        with st.form("delete_status_type_form"):
            if status_types:
                status_to_delete = st.selectbox("בחר סטטוס פעולה למחיקה", status_types)
                submit_button = st.form_submit_button("מחק סטטוס פעולה")
                
                if submit_button and status_to_delete:
                    status_data["סטטוסי פעולה"].remove(status_to_delete)
                    save_status(status_data)
                    st.success(f"סטטוס הפעולה '{status_to_delete}' נמחק בהצלחה")
                    st.rerun()
            else:
                st.info("אין סטטוסי פעולה למחיקה")
                st.form_submit_button("מחק סטטוס פעולה", disabled=True)
    
    elif manage_option == "גיבוי נתונים":
        st.header("גיבוי נתונים")
        
        st.subheader("הורדת קבצי מערכת")
        st.write("לחץ על הכפתור למטה כדי להוריד את כל קבצי ה-JSON של המערכת כקובץ ZIP:")
        
        # יצירת קישור להורדת כל קבצי ה-JSON
        download_link = create_zip_download_link()
        st.markdown(download_link, unsafe_allow_html=True)
        
        st.info("הקובץ יכיל את: נתוני הלקוחות, סוגי המוצרים וסטטוסי הפעולה העדכניים ביותר.")
        
        # מידע על קבצי המערכת
        st.subheader("מידע על קבצי המערכת")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**מספר לקוחות במערכת:**", len(data.keys()))
            st.write("**מספר סוגי מוצרים:**", len(products_data.get("סוגי מוצרים", [])))
            st.write("**מספר סטטוסי פעולה:**", len(status_data.get("סטטוסי פעולה", [])))
        
        with col2:
            client_file_size = os.path.getsize(DATA_FILE) / 1024 if os.path.exists(DATA_FILE) else 0
            products_file_size = os.path.getsize(PRODUCTS_FILE) / 1024 if os.path.exists(PRODUCTS_FILE) else 0
            status_file_size = os.path.getsize(STATUS_FILE) / 1024 if os.path.exists(STATUS_FILE) else 0
            
            st.write(f"**גודל קובץ לקוחות:** {client_file_size:.2f} KB")
            st.write(f"**גודל קובץ מוצרים:** {products_file_size:.2f} KB")
            st.write(f"**גודל קובץ סטטוסים:** {status_file_size:.2f} KB")
            st.write(f"**גודל כולל:** {(client_file_size + products_file_size + status_file_size):.2f} KB")
    
    elif choice in menu:
        # קוד לטיפול בשלבים השונים
        if choice == "שיחת טלפון - מתעניין חדש":
            st.header("שיחת טלפון - הוספת מתעניין חדש")
            
            with st.form("new_client_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    client_name = st.text_input("שם מתעניין")
                    company_name = st.text_input("שם חברה")
                    phone = st.text_input("טלפון מתעניין")
                    
                with col2:
                    address = st.text_input("כתובת פיסית")
                    # קבלת רשימת סוגי המוצרים
                    product_types = products_data.get("סוגי מוצרים", [])
                    product_type = st.selectbox("סוג המוצר", product_types)
                    
                has_needs = st.radio("האם יש:", ["כמויות", "צורך במדידה"])
                
                submit_button = st.form_submit_button("שמור פרטי מתעניין")
                
                if submit_button and client_name:
                    # בדיקה אם הלקוח כבר קיים
                    if client_name in data:
                        st.warning(f"מתעניין בשם {client_name} כבר קיים במערכת")
                    else:
                        # יצירת רשומה חדשה
                        data[client_name] = {
                            "שיחת טלפון": {
                                "שם מתעניין": client_name,
                                "שם חברה": company_name,
                                "טלפון מתעניין": phone,
                                "כתובת פיסית": address,
                                "סוג המוצר": product_type,
                                "האם יש": has_needs
                            }
                        }
                        
                        save_data(data)
                        st.success(f"נוסף בהצלחה: {client_name}")
            
            # הצגת טבלת לקוחות
            if data:
                st.subheader("רשימת מתעניינים:")
                clients_df = []
                
                for name, info in data.items():
                    if "שיחת טלפון" in info:
                        client_info = info["שיחת טלפון"]
                        clients_df.append({
                            "שם מתעניין": name,
                            "טלפון": client_info.get("טלפון מתעניין", ""),
                            "חברה": client_info.get("שם חברה", ""),
                            "כתובת": client_info.get("כתובת פיסית", ""),
                            "סוג מוצר": client_info.get("סוג המוצר", "")
                        })
                
                if clients_df:
                    st.dataframe(pd.DataFrame(clients_df))
        
        elif choice == "פגישה/דוגמאות":
            st.header("פגישה/דוגמאות")
            
            # בחירת לקוח מהרשימה
            selected_client = st.selectbox("בחר מתעניין", client_names if client_names else ["אין מתעניינים במערכת"])
            
            if selected_client and selected_client != "אין מתעניינים במערכת":
                with st.form("meetings_samples_form"):
                    samples_needed = st.radio("האם דרושות דוגמאות", ["כן", "לא"])
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        meeting_date = st.date_input("תאריך לפגישה", datetime.now(), format="DD/MM/YYYY")
                        
                    with col2:
                        meeting_time = st.time_input("שעה", datetime.strptime("10:30", "%H:%M"))
                        
                    submit_button = st.form_submit_button("שמור פרטי פגישה")
                    
                    if submit_button:
                        meeting_datetime = format_datetime(meeting_date.strftime("%d/%m/%Y"), meeting_time.strftime("%H:%M"))
                        
                        # עדכון נתוני הלקוח
                        if "פגישה/דוגמאות" not in data[selected_client]:
                            data[selected_client]["פגישה/דוגמאות"] = {}
                        
                        data[selected_client]["פגישה/דוגמאות"].update({
                            "האם דרושות דוגמאות": samples_needed,
                            "תאריך לפגישה": meeting_datetime
                        })
                        
                        save_data(data)
                        st.success(f"פרטי פגישה נשמרו בהצלחה: {selected_client}")
                
                # הצגת מידע קיים
                if "פגישה/דוגמאות" in data[selected_client]:
                    meeting_info = data[selected_client]["פגישה/דוגמאות"]
                    st.subheader("פרטי פגישה קיימים:")
                    
                    for key, value in meeting_info.items():
                        st.write(f"**{key}:** {value}")
        
        elif choice == "הצעת מחיר":
            st.header("הצעת מחיר")
            
            # בחירת לקוח מהרשימה
            selected_client = st.selectbox("בחר מתעניין", client_names if client_names else ["אין מתעניינים במערכת"])
            
            if selected_client and selected_client != "אין מתעניינים במערכת":
                with st.form("price_proposal_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        proposal_number = st.text_input("מספר הצעת המחיר")
                        proposal_amount = st.number_input("סכום הצעת מחיר", min_value=0, value=10000)
                        
                    with col2:
                        is_approved = st.radio("האם יצאה הצעה?", ["כן", "לא"])
                    
                    submit_button = st.form_submit_button("שמור פרטי הצעת מחיר")
                    
                    if submit_button:
                        # עדכון נתוני הלקוח
                        if "הצעת מחיר" not in data[selected_client]:
                            data[selected_client]["הצעת מחיר"] = {}
                        
                        data[selected_client]["הצעת מחיר"].update({
                            "מספר הצעת המחיר": proposal_number,
                            "סכום הצעת מחיר": f"{proposal_amount} ש\"ח",
                            "האם יצאה הצעה?": is_approved
                        })
                        
                        save_data(data)
                        st.success(f"פרטי הצעת מחיר נשמרו בהצלחה: {selected_client}")
                
                # הצגת מידע קיים
                if "הצעת מחיר" in data[selected_client]:
                    proposal_info = data[selected_client]["הצעת מחיר"]
                    st.subheader("פרטי הצעת מחיר קיימים:")
                    
                    for key, value in proposal_info.items():
                        st.write(f"**{key}:** {value}")
        
        elif choice == "אישור הזמנה":
            st.header("אישור הזמנה")
            
            # בחירת לקוח מהרשימה
            selected_client = st.selectbox("בחר מתעניין", client_names if client_names else ["אין מתעניינים במערכת"])
            
            if selected_client and selected_client != "אין מתעניינים במערכת":
                with st.form("order_approval_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        approval_date = st.date_input("תאריך אישור", datetime.now(), format="DD/MM/YYYY")
                        
                    with col2:
                        down_payment = st.number_input("מקדמה", min_value=0, value=3000)
                        
                    submit_button = st.form_submit_button("שמור פרטי אישור הזמנה")
                    
                    if submit_button:
                        approval_date_str = approval_date.strftime("%d/%m/%Y")
                        
                        # עדכון נתוני הלקוח
                        if "אישור הזמנה" not in data[selected_client]:
                            data[selected_client]["אישור הזמנה"] = {}
                        
                        data[selected_client]["אישור הזמנה"].update({
                            "תאריך אישור": approval_date_str,
                            "מקדמה": f"{down_payment} ש\"ח"
                        })
                        
                        save_data(data)
                        st.success(f"פרטי אישור הזמנה נשמרו בהצלחה: {selected_client}")
                
                # הצגת מידע קיים
                if "אישור הזמנה" in data[selected_client]:
                    approval_info = data[selected_client]["אישור הזמנה"]
                    st.subheader("פרטי אישור הזמנה קיימים:")
                    
                    for key, value in approval_info.items():
                        st.write(f"**{key}:** {value}")
        
        elif choice == "רכש ויבוא":
            st.header("רכש ויבוא")
            
            # בחירת לקוח מהרשימה
            selected_client = st.selectbox("בחר מתעניין", client_names if client_names else ["אין מתעניינים במערכת"])
            
            if selected_client and selected_client != "אין מתעניינים במערכת":
                with st.form("purchase_import_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        materials_type = st.text_input("פרטי חומר גלם")
                        
                    with col2:
                        import_date = st.date_input("מועד הגעת החומרים לארץ", datetime.now(), format="DD/MM/YYYY")
                        
                    submit_button = st.form_submit_button("שמור פרטי רכש ויבוא")
                    
                    if submit_button:
                        import_date_str = import_date.strftime("%d/%m/%Y")
                        
                        # עדכון נתוני הלקוח
                        if "רכש ויבוא" not in data[selected_client]:
                            data[selected_client]["רכש ויבוא"] = {}
                        
                        data[selected_client]["רכש ויבוא"].update({
                            "פרטי חומר גלם": materials_type,
                            "תאריך יבוא": import_date_str
                        })
                        
                        save_data(data)
                        st.success(f"פרטי רכש ויבוא נשמרו בהצלחה: {selected_client}")
                
                # הצגת מידע קיים
                if "רכש ויבוא" in data[selected_client]:
                    import_info = data[selected_client]["רכש ויבוא"]
                    st.subheader("פרטי רכש ויבוא קיימים:")
                    
                    for key, value in import_info.items():
                        st.write(f"**{key}:** {value}")
        
        elif choice == "בדיקת האתר":
            st.header("בדיקת האתר")
            
            # בחירת לקוח מהרשימה
            selected_client = st.selectbox("בחר מתעניין", client_names if client_names else ["אין מתעניינים במערכת"])
            
            if selected_client and selected_client != "אין מתעניינים במערכת":
                with st.form("site_verification_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        is_ready = st.radio("האם האתר מוכן להתקנה", ["כן", "לא"])
                        
                    with col2:
                        verification_date = st.date_input("מועד בדיקת האתר", datetime.now(), format="DD/MM/YYYY")
                        
                    submit_button = st.form_submit_button("שמור פרטי בדיקת האתר")
                    
                    if submit_button:
                        verification_date_str = verification_date.strftime("%d/%m/%Y")
                        
                        # עדכון נתוני הלקוח
                        if "בדיקת האתר" not in data[selected_client]:
                            data[selected_client]["בדיקת האתר"] = {}
                        
                        data[selected_client]["בדיקת האתר"].update({
                            "האם האתר מוכן להתקנה": is_ready,
                            "תאריך בדיקה": verification_date_str
                        })
                        
                        save_data(data)
                        st.success(f"פרטי בדיקת האתר נשמרו בהצלחה: {selected_client}")
                
                # הצגת מידע קיים
                if "בדיקת האתר" in data[selected_client]:
                    verification_info = data[selected_client]["בדיקת האתר"]
                    st.subheader("פרטי בדיקת האתר קיימים:")
                    
                    for key, value in verification_info.items():
                        st.write(f"**{key}:** {value}")
        
        elif choice == "התקנה וגבייה":
            st.header("התקנה וגבייה")
            
            # בחירת לקוח מהרשימה
            selected_client = st.selectbox("בחר מתעניין", client_names if client_names else ["אין מתעניינים במערכת"])
            
            if selected_client and selected_client != "אין מתעניינים במערכת":
                with st.form("installation_payment_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        installation_date = st.date_input("תאריך התקנה", datetime.now(), format="DD/MM/YYYY")
                        installation_time = st.time_input("שעת התקנה", datetime.strptime("08:00", "%H:%M"))
                        
                    with col2:
                        remaining_payment = st.number_input("סכום לתשלום שנותר", min_value=0, value=7000)
                        payment_type = st.selectbox("סוג תשלום", ["העברה בנקאית", "צ'ק", "מזומן", "כרטיס אשראי"])
                        
                    submit_button = st.form_submit_button("שמור פרטי התקנה וגבייה")
                    
                    if submit_button:
                        installation_datetime = format_datetime(installation_date.strftime("%d/%m/%Y"), installation_time.strftime("%H:%M"))
                        
                        # עדכון נתוני הלקוח
                        if "התקנה וגבייה" not in data[selected_client]:
                            data[selected_client]["התקנה וגבייה"] = {}
                        
                        data[selected_client]["התקנה וגבייה"].update({
                            "תאריך התקנה": installation_datetime,
                            "סכום לתשלום": f"{remaining_payment} ש\"ח",
                            "סוג תשלום": payment_type
                        })
                        
                        save_data(data)
                        st.success(f"פרטי התקנה וגבייה נשמרו בהצלחה: {selected_client}")
                
                # הצגת מידע קיים
                if "התקנה וגבייה" in data[selected_client]:
                    installation_info = data[selected_client]["התקנה וגבייה"]
                    st.subheader("פרטי התקנה וגבייה קיימים:")
                    
                    for key, value in installation_info.items():
                        st.write(f"**{key}:** {value}")
        
        elif choice == "מעקב ותזכורות":
            st.header("מעקב ותזכורות")
            
            # בחירת לקוח מהרשימה
            selected_client = st.selectbox("בחר מתעניין", client_names if client_names else ["אין מתעניינים במערכת"])
            
            if selected_client and selected_client != "אין מתעניינים במערכת":
                # טופס תזכורת
                with st.form("followup_reminders_form"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        reminder_text = st.text_area("תזכורת לפעולה")
                    
                    with col2:
                        reminder_date = st.date_input("תאריך תזכורת", datetime.now(), format="DD/MM/YYYY")
                        
                    with col3:
                        reminder_time = st.time_input("שעת תזכורת", datetime.strptime("09:00", "%H:%M"))
                        
                    # סטטוס פעולה (מתוך קובץ סטטוסים)
                    status_options = status_data.get("סטטוסי פעולה", ["יושם", "בתהליך", "תקוע"])
                    payment_status = st.selectbox("סטטוס פעולה", status_options)
                    
                    # הערות למעקב (הועבר מהערות למעקב)
                    notes = st.text_area("הערות למעקב")
                    
                    submit_button = st.form_submit_button("שמור")
                    
                    if submit_button:
                        reminder_datetime = format_datetime(reminder_date.strftime("%d/%m/%Y"), reminder_time.strftime("%H:%M"))
                        
                        # עדכון נתוני הלקוח - מעקב ותזכורות
                        if "מעקב ותזכורות" not in data[selected_client]:
                            data[selected_client]["מעקב ותזכורות"] = {}
                        
                        # עדכון נתוני הלקוח - סטטוס פעולה
                        if "סטטוס פעולה" not in data[selected_client]:
                            data[selected_client]["סטטוס פעולה"] = {}
                        
                        # עדכון נתוני הלקוח - הערות למעקב
                        if "הערות למעקב" not in data[selected_client]:
                            data[selected_client]["הערות למעקב"] = {}
                        
                        data[selected_client]["מעקב ותזכורות"].update({
                            "תזכורת לפעולה": reminder_text,
                            "תאריך תזכורת": reminder_datetime
                        })
                        
                        data[selected_client]["סטטוס פעולה"].update({
                            "סטטוס": payment_status
                        })
                        
                        data[selected_client]["הערות למעקב"].update({
                            "הערות": notes
                        })
                        
                        save_data(data)
                        st.success(f"מידע המעקב נשמר בהצלחה: {selected_client}")
                
                # הצגת מידע קיים
                tabs = st.tabs(["תזכורות", "סטטוס פעולה", "הערות למעקב"])
                
                with tabs[0]:
                    if "מעקב ותזכורות" in data[selected_client]:
                        reminder_info = data[selected_client]["מעקב ותזכורות"]
                        st.subheader("תזכורות קיימות:")
                        for key, value in reminder_info.items():
                            st.write(f"**{key}:** {value}")
                
                with tabs[1]:
                    if "סטטוס פעולה" in data[selected_client]:
                        status_info = data[selected_client]["סטטוס פעולה"]
                        st.subheader("סטטוס קיים:")
                        for key, value in status_info.items():
                            st.write(f"**{key}:** {value}")
                
                with tabs[2]:
                    if "הערות למעקב" in data[selected_client]:
                        notes_info = data[selected_client]["הערות למעקב"]
                        st.subheader("הערות קיימות:")
                        for key, value in notes_info.items():
                            st.write(f"**{key}:** {value}")
    
    else:
        # הצגת הדשבורד הראשי
        st.header("דשבורד הצעות מחיר")
        
        # חלוקת המסך לטורים
        col1, col2 = st.columns(2)
        
        with col1:
            # יצירת גרף עוגה לפי סטטוס
            if not df_proposals.empty:
                status_counts = df_proposals["סטטוס"].value_counts().reset_index()
                status_counts.columns = ["סטטוס", "כמות"]
                
                # מיפוי צבעים
                color_map = {
                    "לא נשלחה": "red",
                    "נשלחה": "orange",
                    "מאושרת": "green"
                }
                
                fig_pie = px.pie(
                    status_counts,
                    values="כמות",
                    names="סטטוס",
                    title="התפלגות סטטוס הצעות מחיר",
                    color="סטטוס",
                    color_discrete_map=color_map
                )
                fig_pie.update_traces(textinfo="percent+label")
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("אין מספיק נתונים להצגת הגרף")
        
        with col2:
            # יצירת גרף עמודות לפי סכומי הצעות המחיר
            if not df_proposals.empty and df_proposals["סכום"].sum() > 0:
                # סינון לקוחות שיש להם הצעת מחיר
                df_with_proposals = df_proposals[df_proposals["סכום"] > 0]
                
                # מיפוי צבעים לפי סטטוס
                colors = [
                    "red" if status == "לא נשלחה" else 
                    "orange" if status == "נשלחה" else 
                    "green" 
                    for status in df_with_proposals["סטטוס"]
                ]
                
                fig_bar = go.Figure()
                fig_bar.add_trace(go.Bar(
                    x=df_with_proposals["שם לקוח"],
                    y=df_with_proposals["סכום"],
                    marker_color=colors,
                    text=df_with_proposals["סכום"],
                    textposition="auto"
                ))
                
                fig_bar.update_layout(
                    title="סכומי הצעות מחיר לפי לקוח",
                    xaxis_title="שם לקוח",
                    yaxis_title="סכום (ש\"ח)"
                )
                
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("אין מספיק נתונים להצגת הגרף")
        
        # טבלת לקוחות וסטטוס הצעות מחיר
        st.subheader("פירוט הצעות מחיר")
        
        if not df_proposals.empty:
            # הוספת עיצוב צבעוני לטבלה
            def highlight_status(val):
                if val == "לא נשלחה":
                    return 'background-color: rgba(255, 0, 0, 0.2)'
                elif val == "נשלחה":
                    return 'background-color: rgba(255, 165, 0, 0.2)'
                elif val == "מאושרת":
                    return 'background-color: rgba(0, 128, 0, 0.2)'
                return ''
            
            # ארגון מחדש של עמודות הטבלה
            display_df = df_proposals[["שם לקוח", "סטטוס", "סכום"]].copy()
            display_df["סכום"] = display_df["סכום"].apply(lambda x: f"{x:,} ש\"ח" if x > 0 else "-")
            
            # הצגת טבלה מעוצבת
            st.dataframe(
                display_df.style.applymap(highlight_status, subset=["סטטוס"]),
                use_container_width=True
            )
        else:
            st.info("אין לקוחות במערכת")
        
        # קישור לשלבים השונים
        st.markdown("---")
        st.subheader("קישורים מהירים")
        
        quick_links_col1, quick_links_col2, quick_links_col3 = st.columns(3)
        
        with quick_links_col1:
            if st.button("שיחת טלפון - מתעניין חדש"):
                st.query_params.page = "new_client"
                st.rerun()
        
        with quick_links_col2:
            if st.button("הצעת מחיר"):
                st.query_params.page = "price_proposal"
                st.rerun()
        
        with quick_links_col3:
            if st.button("מעקב ותזכורות"):
                st.query_params.page = "followup"
                st.rerun()
    
    # הצגת כל המידע על לקוח נבחר
    st.sidebar.markdown("---")
    st.sidebar.subheader("צפייה במידע מלא על לקוח")
    view_client = st.sidebar.selectbox("בחר לקוח לצפייה", client_names if client_names else ["אין לקוחות במערכת"], key="view_client")
    
    if view_client and view_client != "אין לקוחות במערכת":
        st.sidebar.markdown("---")
        if st.sidebar.button("הצג מידע מלא"):
            st.header(f"מידע מלא עבור: {view_client}")
            
            # הצגת כל המידע על הלקוח
            for category, info in data[view_client].items():
                st.subheader(category)
                
                for key, value in info.items():
                    st.write(f"**{key}:** {value}")
                
                st.markdown("---")

if __name__ == "__main__":
    main()