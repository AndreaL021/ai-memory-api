from enum import Enum


class SecurityLevel(str, Enum):
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    SECRET_REFERENCE = "secret_reference"
    BLOCKED_SECRET = "blocked_secret"


DEFAULT_SECURITY_LEVEL = SecurityLevel.CONFIDENTIAL

SECURITY_LEVEL_DEFINITIONS = {
    SecurityLevel.CONFIDENTIAL: {
        "description": "Default private memory available to authorized consumers.",
        "can_store_normal_memory": True,
        "requires_redaction": False,
    },
    SecurityLevel.RESTRICTED: {
        "description": "Sensitive user, project, or business context requiring stricter access controls.",
        "can_store_normal_memory": True,
        "requires_redaction": False,
    },
    SecurityLevel.SECRET_REFERENCE: {
        "description": "Pointer to a secret stored outside normal memory text.",
        "can_store_normal_memory": True,
        "requires_redaction": True,
    },
    SecurityLevel.BLOCKED_SECRET: {
        "description": "Raw secret material that must not be stored as normal memory text.",
        "can_store_normal_memory": False,
        "requires_redaction": True,
    },
}


SENSITIVE_MEMORY_TYPES = {
    "credential_reference",
    "decision",
    "fact",
    "plan",
}


def classify_security_level(
    memory_type: str | None = None,
    contains_secret: bool = False,
    contains_sensitive_data: bool = False,
):
    if contains_secret:
        return SecurityLevel.BLOCKED_SECRET

    if memory_type == "credential_reference":
        return SecurityLevel.SECRET_REFERENCE

    if contains_sensitive_data or memory_type in SENSITIVE_MEMORY_TYPES:
        return SecurityLevel.RESTRICTED

    return DEFAULT_SECURITY_LEVEL
