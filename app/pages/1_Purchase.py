import streamlit as st
from settings import LS_CHECKOUT_URL

st.set_page_config(page_title="Acquista licenza", page_icon="🛒")

st.title("Acquista o rinnova la licenza")
st.write(
    "Per acquistare o rinnovare la licenza MaLu Hub Route, clicca il pulsante qui sotto."
)

st.link_button("Vai al checkout", LS_CHECKOUT_URL, use_container_width=True)

st.info(
    "Se hai già acquistato, controlla l'email che contiene la tua chiave licenza Lemon Squeezy."
)
