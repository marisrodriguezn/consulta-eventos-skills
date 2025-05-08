import streamlit as st
import pandas as pd
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

# ---- TÍTULO ----
st.title("📋 Consulta tu inscripción a eventos Skills Academy")

# ---- CONFIGURACIÓN DE GOOGLE SHEETS ----
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Leer credenciales desde secrets
creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# ID de tu archivo Google Sheets (de la URL)
SHEET_ID = "PEGAR_AQUI_ID_DEL_DOCUMENTO"
SHEET_NAME = "Sheet1"
worksheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

# Cargar datos
data = worksheet.get_all_records()
df = pd.DataFrame(data)

# ---- ENTRADA DE CORREO ----
correo_input = st.text_input("✉️ Ingresa tu correo electrónico para ver tus inscripciones:")

if st.button("Consultar"):
    correo = correo_input.strip().lower()
    resultado = df[df["Mail"].str.lower() == correo]

    if resultado.empty:
        st.warning("❌ Correo no encontrado. Verifica que esté bien escrito.")
    else:
        st.success("✅ Estos son tus eventos:")
        eventos = ["AUTENTICIDAD", "RELEVANCIA", "CONEXIÓN", "STORYTELLING", "C.DIFICILES", "C.PRESENTACIONES"]
        fechas_df = df[["Modulo", "Fecha"]].dropna().drop_duplicates().set_index("Modulo")

        resumen = []
        for evento in eventos:
            estado = resultado.iloc[0][evento]
            fecha = fechas_df.loc[evento, "Fecha"] if evento in fechas_df.index else "No disponible"
            resumen.append({"Evento": evento, "Estado": estado, "Fecha": fecha})

        st.dataframe(pd.DataFrame(resumen), use_container_width=True)
