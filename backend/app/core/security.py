def mask_secret(value: str | None, visible_chars: int = 4) -> str:
    if not value:
        return "<not set>"
    if len(value) <= visible_chars:
        return "*" * len(value)
    return "*" * (len(value) - visible_chars) + value[-visible_chars:]