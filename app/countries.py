# app/countries.py
from typing import Optional

# EU member states (as of Oct 2025)
EU_ALPHA2 = {
    "AT","BE","BG","HR","CY","CZ","DK","EE","FI","FR",
    "DE","GR","HU","IE","IT","LV","LT","LU","MT","NL",
    "PL","PT","RO","SK","SI","ES","SE"
}

EU_NAMES_EN = {
    "Austria","Belgium","Bulgaria","Croatia","Cyprus","Czechia","Czech Republic",
    "Denmark","Estonia","Finland","France","Germany","Greece","Hungary",
    "Ireland","Italy","Latvia","Lithuania","Luxembourg","Malta",
    "Netherlands","The Netherlands","Poland","Portugal","Romania",
    "Slovakia","Slovenia","Spain","Sweden"
}

EU_NAMES_IT = {
    "Austria":"Austria",
    "Belgium":"Belgio",
    "Bulgaria":"Bulgaria",
    "Croatia":"Croazia",
    "Cyprus":"Cipro",
    "Czechia":"Cechia",
    "Czech Republic":"Repubblica Ceca",
    "Denmark":"Danimarca",
    "Estonia":"Estonia",
    "Finland":"Finlandia",
    "France":"Francia",
    "Germany":"Germania",
    "Greece":"Grecia",
    "Hungary":"Ungheria",
    "Ireland":"Irlanda",
    "Italy":"Italia",
    "Latvia":"Lettonia",
    "Lithuania":"Lituania",
    "Luxembourg":"Lussemburgo",
    "Malta":"Malta",
    "Netherlands":"Paesi Bassi",
    "The Netherlands":"Paesi Bassi",
    "Poland":"Polonia",
    "Portugal":"Portogallo",
    "Romania":"Romania",
    "Slovakia":"Slovacchia",
    "Slovenia":"Slovenia",
    "Spain":"Spagna",
    "Sweden":"Svezia",
}

# Esporre una collezione comoda da usare con 'in' per nomi e codici.
EU_COUNTRIES = frozenset(EU_ALPHA2 | set(EU_NAMES_EN) | set(EU_NAMES_IT.values()))

def localize_country_it(country: Optional[str]) -> str:
    """
    Converte un nome di paese o codice ISO alpha-2 in versione italiana.
    Se non riconosciuto, restituisce il valore originale.
    """
    if not country:
        return ""
    c = country.strip()
    up = c.upper()

    # Se è un codice alpha-2 EU, mappa al nome italiano
    if up in EU_ALPHA2:
        alpha2_to_en = {
            "AT":"Austria","BE":"Belgium","BG":"Bulgaria","HR":"Croatia","CY":"Cyprus",
            "CZ":"Czechia","DK":"Denmark","EE":"Estonia","FI":"Finland","FR":"France",
            "DE":"Germany","GR":"Greece","HU":"Hungary","IE":"Ireland","IT":"Italy",
            "LV":"Latvia","LT":"Lithuania","LU":"Luxembourg","MT":"Malta","NL":"Netherlands",
            "PL":"Poland","PT":"Portugal","RO":"Romania","SK":"Slovakia","SI":"Slovenia",
            "ES":"Spain","SE":"Sweden",
        }
        en = alpha2_to_en[up]
        return EU_NAMES_IT.get(en, en)

    # Se è già un nome inglese, traduci
    if c in EU_NAMES_IT:
        return EU_NAMES_IT[c]

    # Se è già in italiano o non è EU, restituisci com'è
    return c
