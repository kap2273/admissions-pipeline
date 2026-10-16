from datetime import datetime

STATE_NAMES = { "MASSACHUSETTS": "MA",
                "NEW HAMPSHIRE": "NH",
                "NEW YORK": "NY",
                "CONNECTICUT": "CT",
                "RHODE ISLAND": "RI",
                "MAINE": "ME",
                "VERMONT": "VT",
                "NEW JERSEY": "NJ",
                "PENNSYLVANIA": "PA",
                "CALIFORNIA": "CA" }


DATE_FORMATS = [ "%Y-%m-%d", "%m/%d/%Y",]

def normalize_name(value):
    if not isinstance(value, str):
        return None
    value = value.strip()
    if value == "":
        return None
    return value.title()

def normalize_email(value):
    if not isinstance(value, str):
        return None
    value = value.strip()
    if value == "":
        return None
    return value.lower()

def normalize_phone(value):
    if not isinstance(value, str):
        return None
    digits = ""
    for c in value:
        if c.isdigit():
            digits += c
    if len(digits) < 10:
        return None
    return digits[-10:]

def normalize_state(value):
    if not isinstance(value, str):
        return None
    value = value.strip().upper()
    if value in STATE_NAMES.values():
        return value
    return STATE_NAMES.get(value)

def normalize_date(value):
    if not isinstance (value,str):
        return None
    value = value.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(value, fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass
    return None
