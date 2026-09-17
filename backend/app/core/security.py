"""
Security-related helpers.

For now: utilities to keep secrets out of logs/error messages.
Auth/JWT logic will be added here in Module 14 (Production Hardening).
"""

def mask_secret(value: str | None, visible_chars: int = 4) -> str:
    """Mask a secret for safe logging, e.g. an API key.

    Example: mask_secret("sk-abcd1234efgh") -> "sk-a...efgh"... actually
    returns "****efgh" style masking with only the last few chars visible.
    """

    if not value:
        return "<not set>"
    if len(value) <= visible_chars:
        return "*" * len(value)
    return "*" * (len(value) - visible_chars) + value[-visible_chars:]