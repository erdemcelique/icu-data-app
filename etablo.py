import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Sayfa konfigürasyonu
st.set_page_config(page_title="ICU Data Entry System", layout="centered")

# --- 1. GÜVENLİK AYARLARI ---
# Not: Gerçek hayatta bu şifreleri "Secrets" içine koymalısın ama şimdilik buradan yönet.
USER_CREDENTIALS = {
    "merkez_admin": "sifre123",
    "ankara_ekip": "ank789",
    "istanbul_ekip": "ist456",
    "izmir_ekip": "izm321"
}

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.title("🔒 Yetkili Veri Giriş Paneli")
        st.info("Lütfen size tanımlanan kullanıcı bilgileriyle giriş yapın.")
        
        user = st.text_input("Kullanıcı Adı")
        pw = st.text_input("Şifre", type="password")
        
        if st.button("Giriş Yap"):
            if user in USER_CREDENTIALS and USER_CREDENTIALS[user] == pw:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ Hatalı kullanıcı adı veya şifre!")
        return False
    return True

# --- 2. ANA UYGULAMA MANTIĞI ---
if check_password():
    # Sidebar üzerinden çıkış yapma imkanı
    st.sidebar.success(f"Giriş Başarılı")
    if st.sidebar.button("Güvenli Çıkış"):
        st.session_state.authenticated = False
        st.rerun()

    st.title("🏥 ICU Prognostic Data Entry")
    st.write("Verileri doldurduktan sonra 'Veriyi Kaydet' butonuna basın.")

    # Google Sheets Bağlantısı
    conn = st.connection("gsheets", type=GSheetsConnection)

    # Form Alanı
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

        submit_button = st.form_submit_button(label="🚀 Veriyi Kaydet")

    if submit_button:
        try:
            # TTL=0 ile cache'i baypas edip en güncel veriyi çekiyoruz
            existing_data = conn.read(worksheet="Sheet1", ttl=0)
            
            # Eğer tablo boşsa başlıkları hazırla
            if existing_data is None or existing_data.empty:
                existing_data = pd.DataFrame(columns=[
                    "Age", "CCI", "SOFA", "Sepsis", "Center", 
                    "Hemoglobin", "Albumin", "Lymphocyte", "Platelet", "CRP", "Unfavorable_Discharge"
                ])

            # Yeni veri satırı
            new_row = pd.DataFrame([{
                "Age": age, "CCI": cci, "SOFA": sofa, "Sepsis": sepsis,
                "Center": center, "Hemoglobin": hb, "Albumin": alb,
                "Lymphocyte": lym, "Platelet": plt, "CRP": crp,
                "Unfavorable_Discharge": out
            }])
            
            # Eski veriyle birleştir
            updated_df = pd.concat([existing_data, new_row], ignore_index=True).dropna(how="all")
            
            # Tabloyu güncelle
            conn.update(worksheet="Sheet1", data=updated_df)
            
            st.success("✅ Veri başarıyla Google Sheets'e eklendi!")
            st.balloons()
            
        except Exception as e:
            st.error(f"⚠️ Bir hata oluştu: {e}")

    # Opsiyonel: Verileri Görme Alanı (Sadece Admin için bile yapılabilir)
    with st.expander("📊 Mevcut Kayıtları Önizle"):
        try:
            view_data = conn.read(worksheet="Sheet1", ttl=0)
            st.dataframe(view_data)
        except:
            st.write("Henüz görüntülenecek veri yok.")
