import requests, math
from typing import List, Tuple

# Import robusto: usa OSRM_BASE_URL, se manca usa OSRM_SERVER
try:
    from settings import OSRM_BASE_URL
except ImportError:
    from settings import OSRM_SERVER as OSRM_BASE_URL

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0088
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2.0)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2.0)**2
    return 2*R*math.asin(math.sqrt(a))

def osrm_table(coords: List[Tuple[float,float]], annotations="duration"):
    coords_q = ";".join([f"{lon},{lat}" for lat,lon in coords])
    url = f"{OSRM_BASE_URL}/table/v1/driving/{coords_q}?annotations={annotations}"
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    return r.json()

def osrm_route(coords: List[Tuple[float,float]], overview="full"):
    coords_q = ";".join([f"{lon},{lat}" for lat,lon in coords])
    url = f"{OSRM_BASE_URL}/route/v1/driving/{coords_q}?overview={overview}&geometries=geojson"
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    return r.json()
