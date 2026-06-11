from enum import Enum


class SecurityLevel(str, Enum):
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    SECRET_REFERENCE = "secret_reference"
    BLOCKED_SECRET = "blocked_secret"


def classify_security_level(
    memory_type: str | None = None,
    contains_secret: bool = False,
    contains_sensitive_data: bool = False,
):
    # Map content risk signals to the security level used by memory records.
    from app.config.security import DEFAULT_SECURITY_LEVEL, SENSITIVE_MEMORY_TYPES

    if contains_secret:
        return SecurityLevel.BLOCKED_SECRET

    if memory_type == "credential_reference":
        return SecurityLevel.SECRET_REFERENCE

    if contains_sensitive_data or memory_type in SENSITIVE_MEMORY_TYPES:
        return SecurityLevel.RESTRICTED

    return DEFAULT_SECURITY_LEVEL
