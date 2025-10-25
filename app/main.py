import xml.etree.ElementTree as ET, pandas as pd, streamlit as st
from settings import APP_NAME, APP_VERSION, COPYRIGHT_TEXT, ADMIN_EMAIL, MAX_POINTS, OSRM_BASE_URL, LS_CHECKOUT_URL
from license import validate_license, get_license_error_message
from countries import EU_COUNTRIES, IT_COUNTRY
from osrm_client import haversine_km, osrm_table, osrm_route
from export import to_excel, to_csv, to_kml

st.set_page_config(APP_NAME, layout="wide", page_icon="app/assets/maluhub_logo.png")

lang = st.sidebar.selectbox("Language / Lingua", ["it","en"], format_func=lambda x: "Italiano" if x=="it" else "English")

col_logo, col_title = st.columns([1,6])
with col_logo:
    try: st.image("app/assets/maluhub_logo.png", width=72)
    except Exception: pass
with col_title:
    st.title(APP_NAME)
st.caption(f"Versione: {APP_VERSION}  •  {COPYRIGHT_TEXT}")

with st.sidebar:
    st.subheader("🔑 " + ("Licenza" if lang=="it" else "License"))
    user_key = st.text_input("Lemon Squeezy key", type="password")
    if st.button("Attiva" if lang=="it" else "Activate", use_container_width=True):
        st.session_state["_license_attempt"] = user_key

if "_license_attempt" in st.session_state:
    ok, plan, err = validate_license(st.session_state["_license_attempt"])
    if not ok:
        st.error(get_license_error_message(err or "invalid", lang=lang))
        st.stop()
    else:
        st.success(("Piano attivo: " if lang=="it" else "Active plan: ") + plan.upper())
else:
    st.info("Inserisci la chiave licenza per continuare." if lang=="it" else "Enter your license key to continue.")
    st.stop()

st.subheader("📥 Upload dati (CSV/XLSX/KML)" if lang=="it" else "📥 Upload data (CSV/XLSX/KML)")
uploaded = st.file_uploader("Seleziona file" if lang=="it" else "Select file", type=["csv","xlsx","kml"])

def parse_kml(file)->pd.DataFrame:
    tree=ET.parse(file); root=tree.getroot()
    ns={"k":"http://www.opengis.net/kml/2.2"}
    points=[]
    for pm in root.findall(".//k:Placemark", ns):
        name=pm.findtext("k:name", default="", namespaces=ns)
        coord=pm.find(".//k:Point/k:coordinates", ns)
        if coord is not None and coord.text:
            parts=coord.text.strip().split(",")
            lon=float(parts[0]); lat=float(parts[1])
            points.append({"name":name,"lat":lat,"lon":lon,"active":True})
    df=pd.DataFrame(points)
    if not df.empty:
        df["Pos"]=range(1,len(df)+1)
    return df

df = pd.DataFrame()
if uploaded:
    if uploaded.name.lower().endswith(".csv"):
        df = pd.read_csv(uploaded)
    elif uploaded.name.lower().endswith(".xlsx"):
        df = pd.read_excel(uploaded)
    else:
        df = parse_kml(uploaded)
    desired = ["Pos","id","name","city","province","country","cap","lat","lon","active"]
    for c in desired:
        if c not in df.columns: df[c]=None
    df["active"] = df["active"].fillna(True)
    if len(df) > MAX_POINTS:
        st.warning((f"Sono stati caricati {len(df)} punti, ma il limite è {MAX_POINTS}. Verranno usati solo i primi {MAX_POINTS}.") if lang=="it" else (f"{len(df)} points uploaded but limit is {MAX_POINTS}. Only first {MAX_POINTS} will be used."))
        df = df.head(MAX_POINTS)
    st.success(("Caricati punti: " if lang=="it" else "Loaded points: ") + str(len(df)))

allowed = IT_COUNTRY if 'plan' in locals() and plan=="basic" else EU_COUNTRIES
st.write(("Paesi consentiti: " if lang=="it" else "Allowed countries: ") + (", ".join(allowed[:5]) + (" ..." if len(allowed)>5 else "")))

show_names = st.toggle("Mostra nomi in mappa" if lang=="it" else "Show names on map", value=False)
show_route = st.toggle("Mostra percorso" if lang=="it" else "Show route", value=False)

if not df.empty:
    st.map(df.rename(columns={"lat":"latitude","lon":"longitude"})[["latitude","longitude"]])

st.subheader("⚙️ Calcolo" if lang=="it" else "⚙️ Compute")
mode = st.radio("Modalità", ["OSRM","Geometrico (haversine)"] if lang=="it" else ["OSRM","Geometric (haversine)"], horizontal=True)
order = df.copy()
if not df.empty and st.button("Calcola" if lang=="it" else "Compute", type="primary"):
    if mode.startswith("Geo") or mode=="Geometric (haversine)":
        pts = order[["lat","lon"]].to_numpy()
        n=len(pts); used=[False]*n; path=[]; i=0
        for _ in range(n):
            used[i]=True; path.append(i)
            best=None; bd=1e9
            for j in range(n):
                if not used[j]:
                    from osrm_client import haversine_km
                    d=haversine_km(tuple(pts[i]), tuple(pts[j]))
                    if d<bd: bd=d; best=j
            if best is None: break
            i=best
        order=order.iloc[path].reset_index(drop=True)
        order["Pos"]=range(1,len(order)+1)
        st.success(("Ordine ricalcolato (geometrico)." if lang=="it" else "Order recomputed (geometric)."))
    else:
        try:
            coords=[(float(r["lat"]), float(r["lon"])) for _,r in order.iterrows()]
            _ = osrm_table(coords)
            order["Pos"]=range(1,len(order)+1)
            st.success(("Rotta calcolata con OSRM." if lang=="it" else "Route computed via OSRM."))
        except Exception as e:
            st.error(("Errore OSRM. Verifica OSRM_BASE_URL: " if lang=="it" else "OSRM error. Check OSRM_BASE_URL: ") + str(e))

from export import to_excel, to_csv, to_kml
if not order.empty:
    st.subheader("💾 Export")
    c1,c2,c3=st.columns(3)
    with c1:
        st.download_button("Export Excel", data=to_excel(order), file_name="malu_route.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    with c2:
        st.download_button("Export CSV", data=to_csv(order), file_name="malu_route.csv", mime="text/csv")
    with c3:
        st.download_button("Export KML", data=to_kml(order), file_name="malu_route.kml", mime="application/vnd.google-earth.kml+xml")

st.sidebar.caption(f"Assistenza: {ADMIN_EMAIL}")
st.sidebar.page_link("app/pages/1_Purchase.py", label=("Acquista licenza" if lang=="it" else "Purchase license"), icon="🛒")
