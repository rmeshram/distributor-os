import re

def normalize_phone_number(phone_str: str) -> str:
    """
    Normalizes a phone number to standard E.164 format (+91XXXXXXXXXX).
    If it's already in E.164, returns it. Strips spaces, dashes, parentheses.
    """
    if not phone_str:
        return ""
    
    # Strip all non-digit characters
    digits = re.sub(r"\D", "", phone_str)
    
    # Standard 10 digits
    if len(digits) == 10:
        return f"+91{digits}"
    # 12 digits starting with 91
    if len(digits) == 12 and digits.startswith("91"):
        return f"+91{digits[2:]}"
    
    # Otherwise, return with a leading '+'
    if phone_str.startswith("+") or not digits:
        return f"+{digits}" if digits else ""
    return f"+{digits}"
