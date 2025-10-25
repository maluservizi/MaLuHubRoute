import requests
from typing import Tuple, Optional
from settings import LS_API_KEY, LS_PRODUCT_IDS

LS_VALIDATE_URL = "https://api.lemonsqueezy.com/v1/licenses/validate"

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
ERROR_MESSAGES = {"invalid": LICENSE_ERROR_INVALID, "expired": LICENSE_ERROR_EXPIRED, "limit": LICENSE_ERROR_LIMIT}

def get_license_error_message(error_type: str, lang: str = "it") -> str:
    return ERROR_MESSAGES.get(error_type, {}).get(lang, ERROR_MESSAGES["invalid"]["it"])

def _headers(api_key: str):
    return {"Authorization": f"Bearer {api_key}", "Accept": "application/vnd.api+json", "Content-Type": "application/json"}

def _infer_plan_from_product_id(product_id: Optional[int]) -> str:
    try:
        pid = int(product_id or -1)
        if pid == int(LS_PRODUCT_IDS.get("europe", -2)): return "europe"
        if pid == int(LS_PRODUCT_IDS.get("basic", -3)): return "basic"
    except Exception:
        pass
    return "basic"

def validate_license(license_key: str) -> Tuple[bool, str, Optional[str]]:
    key = (license_key or "").strip()
    if not key:
        return (False, "basic", "invalid")
    if not LS_API_KEY:
        up = key.upper()
        if up.endswith("EUROPE"): return (True, "europe", None)
        return (True, "basic", None)
    import requests
    try:
        payload = {"data": {"type": "license-validations", "attributes": {"license_key": key}}}
        r = requests.post(LS_VALIDATE_URL, json=payload, headers=_headers(LS_API_KEY), timeout=20)
        if r.status_code >= 400:
            txt = r.text.lower()
            if "activation_limit" in txt: return (False, "basic", "limit")
            if "expired" in txt or "canceled" in txt or "cancelled" in txt or "disabled" in txt: return (False, "basic", "expired")
            return (False, "basic", "invalid")
        data = r.json()
        if not bool(data.get("meta", {}).get("valid")):
            attrs = data.get("data", {}).get("attributes", {})
            status = (attrs.get("status") or attrs.get("state") or "").lower()
            if status in ("expired","canceled","cancelled","inactive","disabled"): return (False, "basic", "expired")
            return (False, "basic", "invalid")
        attrs = data.get("data", {}).get("attributes", {})
        product_id = attrs.get("product_id") or attrs.get("productId")
        plan = _infer_plan_from_product_id(product_id)
        return (True, plan, None)
    except requests.Timeout:
        return (False, "basic", "invalid")
    except Exception:
        return (False, "basic", "invalid")
