import base64
from django import template

register = template.Library()

@register.filter
def urlsafe_base64_encode(value):
    """
    Encodes a string or bytes to URL-safe Base64, removing padding.
    Returns an empty string if the input is invalid or None.
    """
    if value is None:
        return ""
    try:
        if isinstance(value, str):
            value = value.encode('utf-8')  # Convert string to bytes
        elif not isinstance(value, bytes):
            return ""  # Return empty string for non-string, non-bytes inputs
        encoded = base64.urlsafe_b64encode(value).decode('utf-8').rstrip('=')
        return encoded
    except (TypeError, ValueError):
        return ""  # Return empty string if encoding fails