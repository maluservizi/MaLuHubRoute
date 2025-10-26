import os, json, math, pandas as pd, streamlit as st
from settings import APP_NAME, APP_VERSION, MAX_POINTS, ADMIN_EMAIL, COPYRIGHT_TEXT, DEFAULT_LANGUAGE
from license import validate_license, streamlit_show_error
from osrm_client import haversine, osrm_table, osrm_route
from export import export_csv, export_excel, export_kml
from countries import EU_COUNTRIES, localize_country_it

# lingua di default (serve per l'etichetta della pagina)
lang = (DEFAULT_LANGUAGE or "it").lower()

st.set_page_config(APP_NAME, layout="wide", page_icon="app/assets/maluhub_logo.png")
col_logo, col_title = st.columns([1,6])
with col_logo:
    try:
        st.image("app/assets/maluhub_logo.png", width=72)
    except Exception:
        pass
with col_title:
    st.title(APP_NAME)

# --- License gate ---
with st.sidebar:
    st.subheader("Licenza")
    license_key = st.text_input(
        "Chiave licenza (Lemon Squeezy)",
        type="password",
        help="Inserisci la chiave di licenza ricevuta via email."
    )
    ok, plan, err = validate_license(license_key)
    if not ok:
        # messaggio localizzato e stop
        streamlit_show_error(err or "invalid", lang=lang)
        st.stop()

    st.success(f"Piano attivo: {plan.upper()}")

    # paesi abilitati per piano
    if plan == "basic":
        allowed = ["Italia"]
    else:
        allowed = EU_COUNTRIES

    st.divider()
    st.caption(f"Assistenza: {ADMIN_EMAIL}")

    # 🔗 link alla pagina: percorso relativo alla cartella "app", senza "app/"
    st.page_link(
        "pages/1_Purchase.py",
        label=("Acquista licenza" if lang == "it" else "Purchase license"),
        icon="🛒"
    )

st.sidebar.subheader("Dati")
uploaded = st.sidebar.file_uploader("Carica file (CSV/XLSX/KML)", type=["csv","xlsx","kml"])
if "points" not in st.session_state:
    st.session_state["points"] = pd.DataFrame(columns=["Pos","id","name","city","province","country","cap","lat","lon","active"])

def ensure_columns(df: pd.DataFrame) -> pd.DataFrame:
    m = {c.lower():c for c in df.columns}
    def col(*names):
        for n in names:
            if n in m: return m[n]
        return None
    rename = {}
    if col("nome","name","label","titolo","punto"): rename[col("nome","name","label","titolo","punto")] = "name"
    if col("lat","latitude","y"): rename[col("lat","latitude","y")] = "lat"
    if col("lon","lng","long","longitude","x"): rename[col("lon","lng","long","longitude","x")] = "lon"
    if col("comune","city","città","citta"): rename[col("comune","city","città","citta")] = "city"
    if col("prov","provincia","province","admin1"): rename[col("prov","provincia","province","admin1")] = "province"
    if col("country","nazione","paese","stato"): rename[col("country","nazione","paese","stato")] = "country"
    if col("cap","zip"): rename[col("cap","zip")] = "cap"
    if col("id","code","codice"): rename[col("id","code","codice")] = "id"
    df = df.rename(columns=rename)
    for c in ["Pos","id","name","city","province","country","cap","lat","lon","active"]:
        if c not in df.columns: df[c] = pd.NA
    if df["Pos"].isna().all():
        df["Pos"] = range(1, len(df)+1)
    df["active"] = df["active"].fillna(True)
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
    return df[["Pos","id","name","city","province","country","cap","lat","lon","active"]]

def filter_by_plan(df: pd.DataFrame) -> pd.DataFrame:
    if "country" not in df.columns: return df
    return df[df["country"].fillna("").isin(allowed) | df["country"].isna()]

colL, colR = st.columns([2,3])

with colL:
    st.subheader("Punti")
    if uploaded is not None:
        try:
            if uploaded.name.lower().endswith(".csv"):
                df = pd.read_csv(uploaded)
            elif uploaded.name.lower().endswith(".xlsx"):
                df = pd.read_excel(uploaded)
            else:
                # enhanced KML support
                import xml.etree.ElementTree as ET, math
                def _haversine(a,b):
                    R=6371.0088
                    lat1,lon1=a; lat2,lon2=b
                    phi1,phi2=math.radians(lat1),math.radians(lat2)
                    dphi=math.radians(lat2-lat1); dl=math.radians(lon2-lon1)
                    x=math.sin(dphi/2)**2+math.cos(phi1)*math.cos(phi2)*math.sin(dl/2)**2
                    return 2*R*math.asin(math.sqrt(x))
                def _parse_coords(text):
                    pairs=[]
                    for token in text.strip().split():
                        parts=token.split(",")
                        if len(parts)>=2:
                            lon=float(parts[0]); lat=float(parts[1])
                            pairs.append((lat,lon))
                    return pairs
                tree = ET.parse(uploaded); root = tree.getroot()
                ns = {"k":"http://www.opengis.net/kml/2.2"}
                # 1) placemarks
                points=[]
                for pm in root.findall(".//k:Placemark", ns):
                    name = pm.findtext("k:name", default="", namespaces=ns)
                    coord = pm.find(".//k:Point/k:coordinates", ns)
                    if coord is not None and coord.text:
                        latlon = _parse_coords(coord.text)[0]
                        points.append({"name": name, "lat": latlon[0], "lon": latlon[1]})
                df = pd.DataFrame(points)
                # 2) path
                line_coords = None
                ls = root.find(".//k:LineString/k:coordinates", ns)
                if ls is not None and ls.text:
                    line_coords = _parse_coords(ls.text)
                # 3) order by path
                if not df.empty and line_coords:
                    remaining = df.index.tolist()
                    order = []
                    for lat,lon in line_coords:
                        if not remaining: break
                        best_i=None; best_d=1e12
                        for i in remaining:
                            d=_haversine((lat,lon),(float(df.loc[i,"lat"]),float(df.loc[i,"lon"])))
                            if d<best_d: best_d=d; best_i=i
                        order.append(best_i); remaining.remove(best_i)
                    order += remaining
                    df = df.loc[order].reset_index(drop=True)
                    df["Pos"] = range(1, len(df)+1)

            df = ensure_columns(df)
            df = filter_by_plan(df)
            if len(df) > MAX_POINTS:
                st.warning(f"Troppi punti ({len(df)}). Limite: {MAX_POINTS}.")
                df = df.head(MAX_POINTS).copy()
            df = df.reset_index(drop=True)
            st.session_state["points"] = df
            st.success(f"Caricato: {uploaded.name} ({len(df)} punti)")
        except Exception as e:
            st.error(f"Errore import: {e}")

    df = st.session_state["points"]
    edited = st.data_editor(df, num_rows="dynamic", use_container_width=True,
                            column_config={
                                "Pos": st.column_config.NumberColumn(min_value=1, step=1),
                                "active": st.column_config.CheckboxColumn("Attivo")
                            })
    c1,c2,c3,c4 = st.columns(4)
    with c1:
        if st.button("Applica ordine"):
            n = edited.copy()
            n["Pos"] = pd.to_numeric(n["Pos"], errors="coerce").fillna(1).astype(int)
            n = n.sort_values("Pos").reset_index(drop=True)
            n["Pos"] = range(1, len(n)+1)
            st.session_state["points"] = n
            st.success("Ordine applicato.")
    with c2:
        if st.button("Pulisci tutto"):
            st.session_state["points"] = pd.DataFrame(columns=df.columns)
            st.experimental_rerun()
    with c3:
        if st.button("Export CSV"):
            data = export_csv(st.session_state["points"])
            st.download_button("Scarica punti.csv", data, file_name="punti.csv", mime="text/csv")
    with c4:
        if st.button("Export Excel"):
            data = export_excel(st.session_state["points"])
            st.download_button("Scarica punti.xlsx", data, file_name="punti.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

with colR:
    st.subheader("Mappa & Calcolo")
    show_names = st.checkbox("Mostra nomi in mappa", value=False)
    show_route = st.checkbox("Mostra percorso", value=False)
    speed_kmh = st.number_input("Velocità media (km/h) — geometrica", 10, 150, 60)
    mode = st.radio("Modalità", ["Geometrica","OSRM (/table)"], horizontal=True)
    route_coords = None
    if st.button("Calcola percorso"):
        pts = st.session_state["points"]
        pts = pts[pts["active"] == True].dropna(subset=["lat","lon"])
        if len(pts) < 2:
            st.warning("Servono almeno 2 punti con lat/lon.")
        else:
            if mode == "Geometrica":
                order = list(range(len(pts)))
                # nearest neighbor
                used = [False]*len(pts)
                path = []
                cur = 0
                path.append(cur); used[cur]=True
                while len(path) < len(pts):
                    lat1, lon1 = pts.iloc[cur][["lat","lon"]]
                    best, bi = 1e18, None
                    for j in range(len(pts)):
                        if used[j]: continue
                        lat2, lon2 = pts.iloc[j][["lat","lon"]]
                        d = haversine(lat1,lon1,lat2,lon2)
                        if d < best: best, bi = d, j
                    cur = bi; used[cur]=True; path.append(cur)
                route_coords = [(float(pts.iloc[i]["lat"]), float(pts.iloc[i]["lon"])) for i in path]
                distance_km = sum(haversine(route_coords[i][0], route_coords[i][1], route_coords[i+1][0], route_coords[i+1][1]) for i in range(len(route_coords)-1))
                duration_h = distance_km / max(speed_kmh,1)
                st.info(f"Distanza: {distance_km:.1f} km — Durata stimata: {duration_h:.1f} h")
                # update Pos
                ord_pos = pts.index.tolist()
                new = st.session_state["points"].copy()
                new.loc[ord_pos, "Pos"] = range(1, len(ord_pos)+1)
                st.session_state["points"] = new.sort_values("Pos").reset_index(drop=True)
            else:
                coords = [(float(r["lat"]),float(r["lon"])) for _, r in pts.iterrows()]
                try:
                    tbl = osrm_table(coords, annotations="distance,duration")
                    # greedy from 0
                    n = len(coords); used=[False]*n; cur=0; used[0]=True; path=[0]
                    while len(path)<n:
                        best,bi=1e18,None
                        for j in range(n):
                            if used[j]: continue
                            d = tbl["durations"][cur][j] or 1e18
                            if d<best: best,bi=d,j
                        cur=bi; used[cur]=True; path.append(cur)
                    route = osrm_route([coords[i] for i in path])
                    geom = route["routes"][0]["geometry"]["coordinates"]
                    route_coords = [(latlon[1],latlon[0]) for latlon in geom]
                    distance_km = route["routes"][0]["distance"]/1000.0
                    duration_h = route["routes"][0]["duration"]/3600.0
                    st.info(f"Distanza: {distance_km:.1f} km — Durata: {duration_h:.1f} h")
                except Exception as e:
                    st.error(f"OSRM errore: {e}")

    # Map
    try:
        import folium
        from streamlit_folium import st_folium
        m = folium.Map(location=[41.9, 12.5], zoom_start=5)
        pts_plot = st.session_state["points"].dropna(subset=["lat","lon"]).sort_values("Pos")
        for _, r in pts_plot.iterrows():
            label = f"{int(r['Pos']):03d} — {r['name'] or ''}"
            if r.get("city") or r.get("province"):
                label += f" — {r.get('city') or ''} ({r.get('province') or ''})"
            folium.Marker([r["lat"], r["lon"]], tooltip=(label if show_names else None), popup=label).add_to(m)
        if show_route and route_coords and len(route_coords)>=2:
            folium.PolyLine(route_coords, weight=4, opacity=0.8).add_to(m)
        st_folium(m, width=None, height=600)
    except Exception as e:
        st.warning(f"Mappa non disponibile: {e}")

st.caption(f"Versione: {APP_VERSION}  •  {COPYRIGHT_TEXT}")
