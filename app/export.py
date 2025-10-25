import pandas as pd
from io import BytesIO

def to_excel(df: pd.DataFrame) -> bytes:
    buf = BytesIO()
    df.to_excel(buf, index=False)
    return buf.getvalue()

def to_csv(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")

def to_kml(df: pd.DataFrame) -> bytes:
    def pm(row):
        name=row.get("name","")
        lat=row.get("lat"); lon=row.get("lon")
        return f"<Placemark><name>{name}</name><Point><coordinates>{lon},{lat},0</coordinates></Point></Placemark>"
    placemarks="".join(df.apply(pm, axis=1).tolist())
    kml=f'<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2"><Document>{placemarks}</Document></kml>'
    return kml.encode("utf-8")
