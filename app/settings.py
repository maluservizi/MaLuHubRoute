import os
import json

# === Configurazioni base ===
APP_NAME = "MaLu Hub Route"
APP_VERSION = "0.1.0"
COPYRIGHT_TEXT = "© 2025 MaLu Servizi S.r.l. – Tutti i diritti riservati."

# === Limiti operativi ===
MAX_POINTS = 500

# === Email di assistenza ===
ADMIN_EMAIL = "support@maluhub.app"

# === Lemon Squeezy (licenze e checkout) ===
LS_API_KEY = os.getenv("LS_API_KEY", "")
LS_CHECKOUT_URL = os.getenv("LS_CHECKOUT_URL", "https://maluhub.app/checkout")

# Product IDs per piani (basic / europe)
try:
    LS_PRODUCT_IDS = json.loads(os.getenv("LS_PRODUCT_IDS", '{"basic":0,"europe":0}'))
except Exception:
    LS_PRODUCT_IDS = {"basic": 0, "europe": 0}

# === OSRM service ===
OSRM_SERVER = os.getenv("OSRM_SERVER", "https://router.project-osrm.org")

# === lingua di default dell’interfaccia ===
DEFAULT_LANGUAGE = "it"
