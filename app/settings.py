import os, json
APP_NAME = os.getenv("APP_NAME", "MaLu Hub Route")
APP_VERSION = os.getenv("APP_VERSION", "0.1.0")
COPYRIGHT_TEXT = os.getenv("COPYRIGHT_TEXT", "© 2025 MaLu Servizi S.r.l. – Tutti i diritti riservati.")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "support@maluhub.app")
MAX_POINTS = int(os.getenv("MAX_POINTS", "2000"))
OSRM_BASE_URL = os.getenv("OSRM_BASE_URL", "https://osrm.maluhub.app")
DATASET = os.getenv("DATASET", "europe")
LS_API_KEY = os.getenv("LS_API_KEY", "")
try:
    LS_PRODUCT_IDS = json.loads(os.getenv("LS_PRODUCT_IDS", '{"basic":672983,"europe":672960}'))
except Exception:
    LS_PRODUCT_IDS = {"basic": 672983, "europe": 672960}
LS_CHECKOUT_URL = os.getenv("LS_CHECKOUT_URL", "https://maluhub.lemonsqueezy.com")
