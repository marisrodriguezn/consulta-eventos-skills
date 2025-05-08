import streamlit as st
import pandas as pd
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

# ---- TÍTULO ----
st.title("📋 Consulta tu inscripción a eventos Skills Academy")

# ---- CONFIGURACIÓN DE GOOGLE SHEETS ----
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# ID del archivo Google Sheets
SHEET_ID = "1LoCEQq-I2qzfzS94ygig15KJ8U66I1g8DTSeuBUZfYA"

# Cargar hoja de inscripciones
ins_sheet = client.open_by_key(SHEET_ID).worksheet("Inscripciones")
df = pd.DataFrame(ins_sheet.get_all_records())

# Cargar hoja de fechas
fechas_sheet = client.open_by_key(SHEET_ID).worksheet("Fechas")
fechas_df = pd.DataFrame(fechas_sheet.get_all_records())
fechas_df = fechas_df[["Modulo", "Fecha"]].dropna().drop_duplicates().set_index("Modulo")

# Diccionario de nombres completos
nombres_eventos = {
    "AUTENTICIDAD": "AUTENTICIDAD AL COMUNICAR",
    "RELEVANCIA": "RELEVANCIA AL COMUNICAR",
    "CONEXIÓN": "CONEXIÓN AL COMUNICAR",
    "STORYTELLING": "STORYTELLING WORKSHOP",
    "C.DIFICILES": "WORKSHOP CONVERSACIONES DIFÍCILES",
    "C.PRESENTACIONES": "CERTIFICACIÓN PRESENTACIONES EFECTIVAS"
}

# ---- ENTRADA DE CORREO ----
correo_input = st.text_input("✉️ Ingresa tu correo electrónico para ver tus inscripciones:")

if st.button("Consultar"):
    correo = correo_input.strip().lower()
    resultado = df[df["Mail"].str.lower() == correo]

    if resultado.empty:
        st.warning("❌ Correo no encontrado. Verifica que esté bien escrito.")
    else:
        st.info("🎯 A continuación verás tus eventos, estados y fechas.")

        eventos = ["AUTENTICIDAD", "RELEVANCIA", "CONEXIÓN", "STORYTELLING", "C.DIFICILES", "C.PRESENTACIONES"]

        for evento in eventos:
            estado = resultado.iloc[0][evento]
            fecha = fechas_df.loc[evento, "Fecha"] if evento in fechas_df.index else "No disponible"
            color = "#E6F4EA" if "cupo asignado" in estado.lower() else "#F2F2F2"
            emoji = "🎟️" if "cupo asignado" in estado.lower() else "🕐"
            nombre_largo = nombres_eventos.get(evento, evento)

            st.markdown(f"""
                <div style="background-color:{color}; padding:10px 15px; border-radius:8px; margin-bottom:8px; font-size:15px">
                    <div style="font-weight:bold; margin-bottom:4px;">{emoji} {nombre_largo}</div>
                    <div><strong>Estado:</strong> {estado}</div>
                    <div><strong>Fecha:</strong> {fecha}</div>
                </div>
            """, unsafe_allow_html=True)
