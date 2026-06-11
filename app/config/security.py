from app.domain.security_levels import SecurityLevel


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
