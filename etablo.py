import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import streamlit as st

# --- GÜVENLİK AYARLARI ---
USER_CREDENTIALS = {
    "merkez_admin": "sifre123",
    "ankara_ekip": "ank789",
    "istanbul_ekip": "ist456"
}

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.title("🔒 Yetkili Girişi")
        user = st.text_input("Kullanıcı Adı")
        pw = st.text_input("Şifre", type="password")
        if st.button("Giriş Yap"):
            if user in USER_CREDENTIALS and USER_CREDENTIALS[user] == pw:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Hatalı kullanıcı adı veya şifre!")
        return False
    return True

if check_password():
    # --- BURADAN SONRASI SENİN FORM KODLARIN ---
    st.sidebar.button("Çıkış Yap", on_click=lambda: st.session_state.update({"authenticated": False}))
    # (Buraya conn.read, form vs. gelecek...)
st.set_page_config(page_title="ICU Data Entry", layout="centered")
st.title("🏥 ICU Data Entry")

conn = st.connection("gsheets", type=GSheetsConnection)

# Formu tanımla
with st.form(key="icu_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Age", 0, 120, 0)
        cci = st.number_input("CCI", 0, 20, 0)
        sofa = st.number_input("SOFA", 0, 24, 0)
        sepsis = st.selectbox("Sepsis", [0, 1])
        center = st.selectbox("Center", ["Center_A", "Center_B", "Center_C", "Center_D"])
    with col2:
        hb = st.number_input("Hemoglobin", format="%.2f")
        alb = st.number_input("Albumin", format="%.2f")
        lym = st.number_input("Lymphocyte", format="%.2f")
        plt = st.number_input("Platelet", format="%.2f")
        crp = st.number_input("CRP", format="%.2f")
        out = st.selectbox("Unfavorable Discharge", [0, 1])

    submit_button = st.form_submit_button(label="Veriyi Kaydet")

if submit_button:
    # 1. Kaydet butonuna basıldığı an güncel veriyi çek
    df_current = conn.read(worksheet="Sheet1", ttl=0) # ttl=0 önbelleği (cache) temizler
    
    # 2. Eğer tablo boşsa veya hata verdiyse sütunları oluştur
    if df_current is None or df_current.empty:
        df_current = pd.DataFrame(columns=["Age", "CCI", "SOFA", "Sepsis", "Center", "Hemoglobin", "Albumin", "Lymphocyte", "Platelet", "CRP", "Unfavorable_Discharge"])
    
    # 3. Yeni satırı hazırla
    new_row = pd.DataFrame([{
        "Age": age, "CCI": cci, "SOFA": sofa, "Sepsis": sepsis,
        "Center": center, "Hemoglobin": hb, "Albumin": alb,
        "Lymphocyte": lym, "Platelet": plt, "CRP": crp,
        "Unfavorable_Discharge": out
    }])
    
    # 4. Boş satırları ayıklayarak birleştir
    df_updated = pd.concat([df_current, new_row], ignore_index=True).dropna(how="all")
    
    # 5. Tüm listeyi gönder (Tüm tabloyu günceller)
    conn.update(worksheet="Sheet1", data=df_updated)
    
    st.success("Veri başarıyla eklendi!")
    st.balloons()

