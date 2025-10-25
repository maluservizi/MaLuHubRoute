import streamlit as st
from settings import APP_NAME, LS_CHECKOUT_URL, COPYRIGHT_TEXT
st.set_page_config(APP_NAME, layout="centered", page_icon="app/assets/maluhub_logo.png")
st.title("🛒 Acquista licenza / Purchase license")
st.write("Apri il checkout ufficiale Lemon Squeezy per acquistare una licenza di MaLu Hub Route.")
st.link_button("Vai al checkout (Lemon Squeezy)", LS_CHECKOUT_URL)
st.caption(COPYRIGHT_TEXT)
