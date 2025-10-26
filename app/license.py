import os
import requests
from typing import Tuple, Optional

# === Settings (import from settings.py if present) ===
try:
    from settings import LS_API_KEY, LS_PRODUCT_IDS
except Exception:
    LS_API_KEY = os.getenv("LS_API_KEY", "")
    import json
    try:
        LS_PRODUCT_IDS = json.loads(os.getenv("LS_PRODUCT_IDS", '{"basic":0,"europe":0}'))
    except Exception:
        LS_PRODUCT_IDS = {"basic": 0, "europe": 0}

LS_VALIDATE_URL = "https://api.lemonsqueezy.com/v1/licenses/validate"

# ===== Bilingual error messages =====
LICENSE_ERROR_INVALID = {
    "it": "❌ La chiave di licenza inserita non è valida. Controlla di averla copiata correttamente o contatta l’assistenza: support@maluhub.app",
    "en": "❌ The license key you entered is not valid. Please check you copied it correctly or contact support: support@maluhub.app",
}

LICENSE_ERROR_EXPIRED = {
    "it": "⚠️ La tua licenza MaLu Hub Route è scaduta o disattivata. Rinnova l’abbonamento sul sito ufficiale per continuare a usare l’app.",
    "en": "⚠️ Your MaLu Hub Route license has expired or been deactivated. Please renew your subscription on the official website to continue using the app.",
}

LICENSE_ERROR_LIMIT = {
    "it": "🚫 Hai raggiunto il numero massimo di attivazioni per questa licenza. Disattiva una delle installazioni precedenti o contatta l’assistenza per sbloccare un nuovo dispositivo.",
    "en": "🚫 You have reached the maximum number of activations for this license. Please deactivate a previous installation or contact support to unlock a new device.",
}

ERROR_MESSAGES = {
    "invalid": LICENSE_ERROR_INVALID,
    "expired": LICENSE_ERROR_EXPIRED,
    "limit": LICENSE_ERROR_LIMIT,
}


def get_license_error_message(error_type: str, lang: str = "it") -> str:
    """Return localized message for error_type: invalid | expired | limit."""
    return ERROR_MESSAGES.get(error_type, {}).get(lang, ERROR_MESSAGES["invalid"]["it"])


# ===== Internal helpers =====
def _headers():
    return {
        "Authorization": f"Bearer {LS_API_KEY}",
        "Accept": "application/vnd.api+json",
        "Content-Type": "application/json",
    }


def _infer_plan_from_product_id(product_id: Optional[int]) -> str:
    try:
        if product_id is None:
            return "basic"
        pid = int(product_id)
        if pid == int(LS_PRODUCT_IDS.get("europe", -1)):
            return "europe"
        if pid == int(LS_PRODUCT_IDS.get("basic", -2)):
            return "basic"
    except Exception:
        pass
    return "basic"


# ===== Public API =====
def validate_license(license_key: str) -> Tuple[bool, str, Optional[str]]:
    """
    Validate a Lemon Squeezy license key.
    Returns: (ok, plan, error_type)
      - ok: True if valid and usable
      - plan: "basic" | "europe"
      - error_type: None if ok, otherwise "invalid" | "expired" | "limit"

    Behavior:
      * If LS_API_KEY missing → fallback dev mode.
      * If LS_API_KEY present but the key starts with 'TEST' or ends with 'EUROPE',
        accept it locally for testing (mock activation).
    """
    key = (license_key or "").strip()
    if not key:
        return (False, "basic", "invalid")

    # --- Dev fallback when API key is not configured ---
    if not LS_API_KEY:
        up = key.upper()
        if up.endswith("EUROPE"):
            return (True, "europe", None)
        return (True, "basic", None)
    else:
        # --- Patch: accetta chiavi di test anche se LS_API_KEY è impostata ---
        up = key.upper()
        if up.startswith("TEST") or up.endswith("EUROPE"):
            if up.endswith("EUROPE"):
                return (True, "europe", None)
            return (True, "basic", None)

    try:
        payload = {"data": {"type": "license-validations", "attributes": {"license_key": key}}}
        r = requests.post(LS_VALIDATE_URL, json=payload, headers=_headers(), timeout=20)

        if r.status_code >= 400:
            try:
                err = r.json()
                msg = str(err)
                if "activation_limit" in msg or "activation_limit_reached" in msg:
                    return (False, "basic", "limit")
                if "expired" in msg or "canceled" in msg or "disabled" in msg:
                    return (False, "basic", "expired")
            except Exception:
                pass
            return (False, "basic", "invalid")

        data = r.json()
        valid = bool(data.get("meta", {}).get("valid"))
        if not valid:
            attrs = data.get("data", {}).get("attributes", {})
            status = (attrs.get("status") or attrs.get("state") or "").lower()
            if status in ("expired", "cancelled", "canceled", "inactive", "disabled"):
                return (False, "basic", "expired")
            return (False, "basic", "invalid")

        attrs = data.get("data", {}).get("attributes", {})
        product_id = attrs.get("product_id") or attrs.get("productId")
        plan = _infer_plan_from_product_id(product_id)
        return (True, plan, None)

    except requests.Timeout:
        return (False, "basic", "invalid")
    except Exception:
        return (False, "basic", "invalid")


# ===== Optional: Streamlit helpers =====
def streamlit_show_error(error_type: str, lang: str = "it"):
    """If Streamlit is installed, show a localized error banner."""
    try:
        import streamlit as st
        msg = get_license_error_message(error_type, lang=lang)
        if error_type == "expired":
            st.warning(msg)
        elif error_type == "limit":
            st.error(msg)
        else:
            st.error(msg)
    except Exception:
        pass
