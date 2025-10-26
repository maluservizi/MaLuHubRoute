import streamlit as st
from license import validate_license, streamlit_show_error
from settings import ADMIN_EMAIL

st.set_page_config(
    page_title="MaLu Hub Route",
    page_icon="🚗",
    layout="wide",
)

# === Sidebar: License Gate ===
with st.sidebar:
    st.subheader("🔑 Licenza")

    license_key = st.text_input(
        "Lemon Squeezy key",
        type="password",
        placeholder="Inserisci la chiave licenza",
        help="Inserisci la chiave di licenza ricevuta via email dopo l'acquisto."
    )

    ok, plan, err = validate_license(license_key)

    if not ok:
        streamlit_show_error(err or "invalid", lang="it")
        st.stop()

    st.success(f"Piano attivo: {plan.upper()}")

    # Link pagina acquisto
    st.page_link("pages/1_Purchase.py", label="Acquista licenza", icon="🛒")

    # Info di contatto
    st.caption(f"Assistenza: {ADMIN_EMAIL}")

# === Main content ===
st.title("MaLu Hub Route")
st.caption("Versione: 0.1.0 • © 2025 MaLu Servizi S.r.l. – Tutti i diritti riservati.")

st.divider()

st.header("📤 Upload dati (CSV/XLSX/KML)")

uploaded_file = st.file_uploader(
    "Seleziona file",
    type=["csv", "xlsx", "kml"],
    help="Trascina qui il file con le destinazioni o clicca per scegliere."
)

if uploaded_file:
    st.success("✅ File caricato correttamente.")
else:
    st.info("Carica un file CSV, XLSX o KML per iniziare.")

st.write("Paesi consentiti: Italy, France, Germany, Spain, Portugal ...")

st.toggle("Mostra nomi in mappa")
st.toggle("Mostra percorso")

st.header("⚙️ Calcolo")

mode = st.radio("Modalità", ["OSRM", "Geometrico (haversine)"], horizontal=True)

st.button("Esegui calcolo")

st.divider()
st.caption("© 2025 MaLu Servizi S.r.l. – Tutti i diritti riservati.")