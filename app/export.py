# app/export.py
import io
from typing import List, Dict, Optional, Tuple
import pandas as pd


def export_csv(points_df: pd.DataFrame) -> bytes:
    """Esporta il dataframe come CSV (UTF-8)."""
    return points_df.to_csv(index=False).encode("utf-8")


def export_excel(points_df: pd.DataFrame) -> bytes:
    """Esporta il dataframe come file Excel (OpenXML) e restituisce i bytes."""
    bio = io.BytesIO()
    with pd.ExcelWriter(bio, engine="openpyxl") as writer:
        points_df.to_excel(writer, index=False, sheet_name="Percorso")
    return bio.getvalue()


def _placemark_row(r: Dict) -> str:
    """Crea un Placemark KML per una riga del dataframe (lat/lon obbligatori)."""
    pos = int(r.get("Pos")) if pd.notna(r.get("Pos")) else ""
    name = r.get("name") or ""
    city = r.get("city") or ""
    province = r.get("province") or ""
    address = r.get("address") or ""
    lat = r.get("lat")
    lon = r.get("lon")

    if pd.isna(lat) or pd.isna(lon):
        return ""

    label = f"{pos:03d} - {name}" if name or pos != "" else f"{pos:03d}"
    descr_parts: List[str] = []
    if address:
        descr_parts.append(address)
    if city or province:
        descr_parts.append(f"{city} ({province})" if province else city)
    description = " — ".join(filter(None, descr_parts))

    return (
        f"<Placemark>"
        f"<name>{_xml_escape(label)}</name>"
        f"<description>{_xml_escape(description)}</description>"
        f"<Point><coordinates>{lon},{lat},0</coordinates></Point>"
        f"</Placemark>"
    )


def _xml_escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def export_kml(
    points_df: pd.DataFrame,
    route_coords: Optional[List[Tuple[float, float]]] = None,
) -> bytes:
    """
    Esporta un KML con:
    - un Placemark per ogni punto (lat/lon)
    - una LineString opzionale con le coordinate del percorso (route_coords come lista di (lat, lon))
    """
    # Placemarks dei punti
    placemarks = []
    for r in points_df.to_dict(orient="records"):
        pm = _placemark_row(r)
        if pm:
            placemarks.append(pm)
    pm_xml = "\n".join(placemarks)

    # Linea del percorso
    line_xml = ""
    if route_coords and len(route_coords) >= 2:
        coords = " ".join([f"{lon},{lat},0" for (lat, lon) in route_coords])
        line_xml = (
            "<Placemark>"
            "<name>Percorso</name>"
            "<Style><LineStyle><width>4</width></LineStyle></Style>"
            f"<LineString><coordinates>{coords}</coordinates></LineString>"
            "</Placemark>"
        )

    kml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<kml xmlns="http://www.opengis.net/kml/2.2">\n'
        "<Document>\n"
        f"{pm_xml}\n"
        f"{line_xml}\n"
        "</Document>\n"
        "</kml>"
    )
    return kml.encode("utf-8")
