import streamlit as st
from settings import APP_NAME, APP_VERSION, COPYRIGHT_TEXT
st.set_page_config("Version", layout="centered", page_icon="app/assets/maluhub_logo.png")
st.title("Version")
st.write({"name": APP_NAME, "version": APP_VERSION})
st.caption(COPYRIGHT_TEXT)
