import streamlit as st
from settings import COPYRIGHT_TEXT, APP_VERSION
st.set_page_config("Health", layout="centered", page_icon="app/assets/maluhub_logo.png")
st.title("Health")
st.success("ok")
st.caption(f"Version: {APP_VERSION} • {COPYRIGHT_TEXT}")
