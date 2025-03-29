import streamlit as st
import json
import os
import datetime
import pandas as pd
from datetime import datetime

# הגדרת הקבצי JSON
DATA_DIR = "DATA"
DATA_FILE = os.path.join(DATA_DIR, "clients_data.json")
PRODUCTS_FILE = os.path.join(DATA_DIR, "products.json")

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

# שמירת הנתונים לקובץ JSON
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# שמירת סוגי המוצרים לקובץ JSON
def save_products(products_data):
    with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
        json.dump(products_data, f, ensure_ascii=False, indent=4)

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
    
    # CSS לתמיכה בעברית וסגנון כללי
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
    </style>
    """, unsafe_allow_html=True)
    
    # כותרת ראשית
    st.title("מערכת ניהול מתעניינים")
    
    # יצירת קבצי JSON אם אינם קיימים
    init_json_files()
    
    # טעינת הנתונים
    data = load_data()
    products_data = load_products()
    
    # יצירת תפריט צדדי
    menu = ["שיחת טלפון - מתעניין חדש", 
            "פגישה/דוגמאות", 
            "הצעת מחיר", 
            "אישור הזמנה", 
            "רכש ויבוא", 
            "בדיקת האתר", 
            "התקנה וגבייה",
            "מעקב ותזכורות",
            "סטטוס פעילה",
            "הערות למעקב"]
    
    choice = st.sidebar.selectbox("בחר שלב", menu)
    
    # רשימת לקוחות קיימים
    client_names = list(data.keys())
    
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
                
            has_documents = st.radio("האם יש מסמכים", ["כן, במחשב/מייל", "לא"])
            is_urgent = st.radio("האם יש דרישות דחופות", ["כן, במחשב/מייל", "לא"])
            
            contact_date = st.date_input("תאריך לפגישה", datetime.now())
            contact_time = st.time_input("שעה", datetime.strptime("10:30", "%H:%M"))
            
            submit_button = st.form_submit_button("שמור פרטי מתעניין")
            
            if submit_button and client_name:
                # בדיקה אם הלקוח כבר קיים
                if client_name in data:
                    st.warning(f"מתעניין בשם {client_name} כבר קיים במערכת")
                else:
                    contact_datetime = format_datetime(contact_date.strftime("%d/%m/%Y"), contact_time.strftime("%H:%M"))
                    
                    # יצירת רשומה חדשה
                    data[client_name] = {
                        "שיחת טלפון": {
                            "שם מתעניין": client_name,
                            "שם חברה": company_name,
                            "טלפון מתעניין": phone,
                            "כתובת פיסית": address,
                            "סוג המוצר": product_type,
                            "האם יש מסמכים": has_documents,
                            "האם יש דרישות דחופות": is_urgent,
                            "תאריך לפגישה": contact_datetime
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
                        "תאריך פגישה": client_info.get("תאריך לפגישה", "")
                    })
            
            if clients_df:
                st.dataframe(pd.DataFrame(clients_df))
    
    elif choice == "פגישה/דוגמאות":
        st.header("פגישה/דוגמאות")
        
        # בחירת לקוח מהרשימה
        selected_client = st.selectbox("בחר מתעניין", client_names if client_names else ["אין מתעניינים במערכת"])
        
        if selected_client and selected_client != "אין מתעניינים במערכת":
            with st.form("meetings_samples_form"):
                samples_needed = st.radio("האם דרושות דוגמאות", ["כן, יש צורך לשלוח/להביא דוגמאות", "לא"])
                
                col1, col2 = st.columns(2)
                
                with col1:
                    meeting_date = st.date_input("תאריך לפגישה", datetime.now())
                    price_proposal = st.number_input("סכום הצעת מחיר", min_value=0, value=10000)
                    
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
                        "תאריך לפגישה": meeting_datetime,
                        "סכום הצעת מחיר": f"{price_proposal} ש\"ח"
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
                    proposal_date = st.date_input("תאריך בו הוקם אישור את ההצעה", datetime.now())
                    
                is_approved = st.radio("האם יצאה הצעה?", ["כן", "לא"])
                
                submit_button = st.form_submit_button("שמור פרטי הצעת מחיר")
                
                if submit_button:
                    proposal_date_str = proposal_date.strftime("%d/%m/%Y")
                    
                    # עדכון נתוני הלקוח
                    if "הצעת מחיר" not in data[selected_client]:
                        data[selected_client]["הצעת מחיר"] = {}
                    
                    data[selected_client]["הצעת מחיר"].update({
                        "מספר הצעת המחיר": proposal_number,
                        "סכום הצעת מחיר": f"{proposal_amount} ש\"ח",
                        "תאריך אישור": proposal_date_str,
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
                    approval_date = st.date_input("תאריך אישור", datetime.now())
                    down_payment = st.number_input("מקדמה", min_value=0, value=3000)
                    
                with col2:
                    payment_method = st.selectbox("סוג תשלום", ["העברה בנקאית", "צ'ק", "מזומן", "כרטיס אשראי"])
                    
                submit_button = st.form_submit_button("שמור פרטי אישור הזמנה")
                
                if submit_button:
                    approval_date_str = approval_date.strftime("%d/%m/%Y")
                    
                    # עדכון נתוני הלקוח
                    if "אישור הזמנה" not in data[selected_client]:
                        data[selected_client]["אישור הזמנה"] = {}
                    
                    data[selected_client]["אישור הזמנה"].update({
                        "תאריך אישור": approval_date_str,
                        "מקדמה": f"{down_payment} ש\"ח",
                        "סוג תשלום": payment_method
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
                    materials_type = st.text_input("סוג וכמות החומרים הנדרשים לפרויקט")
                    
                with col2:
                    import_date = st.date_input("מועד הגעת החומרים לארץ", datetime.now())
                    
                submit_button = st.form_submit_button("שמור פרטי רכש ויבוא")
                
                if submit_button:
                    import_date_str = import_date.strftime("%d/%m/%Y")
                    
                    # עדכון נתוני הלקוח
                    if "רכש ויבוא" not in data[selected_client]:
                        data[selected_client]["רכש ויבוא"] = {}
                    
                    data[selected_client]["רכש ויבוא"].update({
                        "סוג וכמות החומרים": materials_type,
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
                    verification_date = st.date_input("מועד בדיקת האתר", datetime.now())
                    verification_time = st.time_input("שעה", datetime.strptime("15:00", "%H:%M"))
                    
                submit_button = st.form_submit_button("שמור פרטי בדיקת האתר")
                
                if submit_button:
                    verification_datetime = format_datetime(verification_date.strftime("%d/%m/%Y"), verification_time.strftime("%H:%M"))
                    
                    # עדכון נתוני הלקוח
                    if "בדיקת האתר" not in data[selected_client]:
                        data[selected_client]["בדיקת האתר"] = {}
                    
                    data[selected_client]["בדיקת האתר"].update({
                        "האם האתר מוכן להתקנה": is_ready,
                        "תאריך בדיקה": verification_datetime
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
                    installation_date = st.date_input("תאריך התקנה", datetime.now())
                    installation_time = st.time_input("שעת התקנה", datetime.strptime("08:00", "%H:%M"))
                    remaining_payment = st.number_input("סכום לתשלום שנותר", min_value=0, value=7000)
                    
                with col2:
                    payment_date = st.date_input("תאריך תשלום הסכום שנותר", datetime.now())
                    payment_time = st.time_input("שעת תשלום", datetime.strptime("08:00", "%H:%M"))
                    payment_type = st.selectbox("סוג תשלום", ["העברה בנקאית", "צ'ק", "מזומן", "כרטיס אשראי"])
                    
                submit_button = st.form_submit_button("שמור פרטי התקנה וגבייה")
                
                if submit_button:
                    installation_datetime = format_datetime(installation_date.strftime("%d/%m/%Y"), installation_time.strftime("%H:%M"))
                    payment_datetime = format_datetime(payment_date.strftime("%d/%m/%Y"), payment_time.strftime("%H:%M"))
                    
                    # עדכון נתוני הלקוח
                    if "התקנה וגבייה" not in data[selected_client]:
                        data[selected_client]["התקנה וגבייה"] = {}
                    
                    data[selected_client]["התקנה וגבייה"].update({
                        "תאריך התקנה": installation_datetime,
                        "תאריך תשלום": payment_datetime,
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
            with st.form("followup_reminders_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    reminder_text = st.text_area("תזכורת לפעולה")
                    
                with col2:
                    reminder_date = st.date_input("תאריך תזכורת", datetime.now())
                    reminder_time = st.time_input("שעת תזכורת", datetime.strptime("09:00", "%H:%M"))
                    
                submit_button = st.form_submit_button("שמור תזכורת")
                
                if submit_button:
                    reminder_datetime = format_datetime(reminder_date.strftime("%d/%m/%Y"), reminder_time.strftime("%H:%M"))
                    
                    # עדכון נתוני הלקוח
                    if "מעקב ותזכורות" not in data[selected_client]:
                        data[selected_client]["מעקב ותזכורות"] = {}
                    
                    data[selected_client]["מעקב ותזכורות"].update({
                        "תזכורת לפעולה": reminder_text,
                        "תאריך תזכורת": reminder_datetime
                    })
                    
                    save_data(data)
                    st.success(f"תזכורת נשמרה בהצלחה: {selected_client}")
            
            # הצגת מידע קיים
            if "מעקב ותזכורות" in data[selected_client]:
                reminder_info = data[selected_client]["מעקב ותזכורות"]
                st.subheader("תזכורות קיימות:")
                
                for key, value in reminder_info.items():
                    st.write(f"**{key}:** {value}")
    
    elif choice == "סטטוס פעילה":
        st.header("סטטוס פעילה")
        
        # בחירת לקוח מהרשימה
        selected_client = st.selectbox("בחר מתעניין", client_names if client_names else ["אין מתעניינים במערכת"])
        
        if selected_client and selected_client != "אין מתעניינים במערכת":
            with st.form("status_form"):
                payment_status = st.text_input("סטטוס התשלום (ישלם/בהמחאה/בנקאי)")
                
                submit_button = st.form_submit_button("שמור סטטוס")
                
                if submit_button:
                    # עדכון נתוני הלקוח
                    if "סטטוס פעילה" not in data[selected_client]:
                        data[selected_client]["סטטוס פעילה"] = {}
                    
                    data[selected_client]["סטטוס פעילה"].update({
                        "סטטוס תשלום": payment_status
                    })
                    
                    save_data(data)
                    st.success(f"סטטוס נשמר בהצלחה: {selected_client}")
            
            # הצגת מידע קיים
            if "סטטוס פעילה" in data[selected_client]:
                status_info = data[selected_client]["סטטוס פעילה"]
                st.subheader("סטטוס קיים:")
                
                for key, value in status_info.items():
                    st.write(f"**{key}:** {value}")
    
    elif choice == "הערות למעקב":
        st.header("הערות למעקב")
        
        # בחירת לקוח מהרשימה
        selected_client = st.selectbox("בחר מתעניין", client_names if client_names else ["אין מתעניינים במערכת"])
        
        if selected_client and selected_client != "אין מתעניינים במערכת":
            with st.form("notes_form"):
                notes = st.text_area("הערות למעקב")
                
                submit_button = st.form_submit_button("שמור הערות")
                
                if submit_button:
                    # עדכון נתוני הלקוח
                    if "הערות למעקב" not in data[selected_client]:
                        data[selected_client]["הערות למעקב"] = {}
                    
                    data[selected_client]["הערות למעקב"].update({
                        "הערות": notes
                    })
                    
                    save_data(data)
                    st.success(f"הערות נשמרו בהצלחה: {selected_client}")
            
            # הצגת מידע קיים
            if "הערות למעקב" in data[selected_client]:
                notes_info = data[selected_client]["הערות למעקב"]
                st.subheader("הערות קיימות:")
                
                for key, value in notes_info.items():
                    st.write(f"**{key}:** {value}")
    
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
    
    # אזור ניהול - חדש
    st.sidebar.markdown("---")
    st.sidebar.subheader("ניהול")
    
    # כפתור לניהול סוגי מוצרים
    if st.sidebar.button("ניהול סוגי מוצרים"):
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
                    st.experimental_rerun()
        
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
                    st.experimental_rerun()
            else:
                st.info("אין סוגי מוצרים למחיקה")
                st.form_submit_button("מחק סוג מוצר", disabled=True)

if __name__ == "__main__":
    main()