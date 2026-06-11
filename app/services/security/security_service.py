from app.config.security import SECURITY_LEVEL_DEFINITIONS
from app.domain.security_levels import classify_security_level
from app.services.security.secret_detection_service import detect_secrets, redact_secrets


def classify_memory_security(
    content: str,
    memory_type: str | None = None,
    contains_sensitive_data: bool = False,
):
    # Choose the storage security level for memory content before persistence.
    secret_matches = detect_secrets(content)

    return classify_security_level(
        memory_type=memory_type,
        contains_secret=bool(secret_matches),
        contains_sensitive_data=contains_sensitive_data,
    )


def validate_normal_memory_content(content: str, memory_type: str | None = None):
    # Return whether content can be stored normally and its redacted safe version.
    security_level = classify_memory_security(
        content=content,
        memory_type=memory_type,
    )
    secret_matches = detect_secrets(content)

    if not SECURITY_LEVEL_DEFINITIONS[security_level]["can_store_normal_memory"]:
        return {
            "can_store": False,
            "security_level": security_level.value,
            "content": redact_secrets(content),
            "secret_count": len(secret_matches),
        }

    return {
        "can_store": True,
        "security_level": security_level.value,
        "content": redact_secrets(content),
        "secret_count": len(secret_matches),
    }
