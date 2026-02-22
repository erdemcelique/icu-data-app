import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="ICU Data Entry", layout="centered")
st.title("🏥 ICU Prognostic Data Entry")

# Bağlantı
conn = st.connection("gsheets", type=GSheetsConnection)

# Form
with st.form(key="icu_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    with col1:
        age = st.number_input("Age", min_value=0, max_value=120, step=1)
        cci = st.number_input("CCI", min_value=0, max_value=20, step=1)
        sofa = st.number_input("SOFA", min_value=0, max_value=24, step=1)
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
    # 1. Önce güncel veriyi o an çek (Başkası veri girdiyse kaybolmasın)
    try:
        existing_data = conn.read(worksheet="Sheet1")
        if existing_data is None:
            existing_data = pd.DataFrame()
    except:
        existing_data = pd.DataFrame()

    # 2. Yeni satırı hazırla
    new_row = pd.DataFrame([{
        "Age": age, "CCI": cci, "SOFA": sofa, "Sepsis": sepsis,
        "Center": center, "Hemoglobin": hb, "Albumin": alb,
        "Lymphocyte": lym, "Platelet": plt, "CRP": crp,
        "Unfavorable_Discharge": out
    }])
    
    # 3. Mevcut veriyle birleştir (dropna ile boş satırları temizle)
    updated_df = pd.concat([existing_data, new_row], ignore_index=True).dropna(how="all")
    
    # 4. TAM listeyi gönder (Update en garanti yoldur ama doğru data ile)
    conn.update(worksheet="Sheet1", data=updated_df)
    
    st.success("Veri başarıyla eklendi!")
    st.balloons()

# Opsiyonel: Tabloyu aşağıda önizle (Veri geliyor mu görmüş olursun)
if st.checkbox("Mevcut Verileri Göster"):
    st.dataframe(conn.read(worksheet="Sheet1"))
