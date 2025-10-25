import requests
from typing import List, Tuple, Dict, Any
from settings import OSRM_BASE_URL

def haversine_km(a: Tuple[float,float], b: Tuple[float,float]) -> float:
    R=6371.0088
    lat1,lon1=a; lat2,lon2=b
    from math import radians, sin, cos, asin, sqrt
    phi1,phi2=radians(lat1),radians(lat2)
    dphi=radians(lat2-lat1); dl=radians(lon2-lon1)
    x=sin(dphi/2)**2+cos(phi1)*cos(phi2)*sin(dl/2)**2
    return 2*R*asin(sqrt(x))

def osrm_table(coords: List[Tuple[float,float]]) -> Dict[str, Any]:
    if not coords: return {}
    coord_str = ";".join([f"{c[1]},{c[0]}" for c in coords])
    url = f"{OSRM_BASE_URL}/table/v1/driving/{coord_str}?annotations=distance,duration"
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    return r.json()

def osrm_route(coords: List[Tuple[float,float]]) -> Dict[str, Any]:
    coord_str = ";".join([f"{c[1]},{c[0]}" for c in coords])
    url=f"{OSRM_BASE_URL}/route/v1/driving/{coord_str}?overview=full&geometries=geojson"
    r=requests.get(url, timeout=60)
    r.raise_for_status()
    return r.json()
