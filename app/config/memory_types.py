from app.domain.memory_types import MemoryType


MEMORY_TYPE_DEFINITIONS = {
    MemoryType.PREFERENCE: {
        "description": "A user preference that should influence future behavior.",
        "default_security_level": "confidential",
    },
    MemoryType.METHOD: {
        "description": "A reusable way of doing something, including workflows, fixes, and lessons learned.",
        "default_security_level": "confidential",
    },
    MemoryType.FACT: {
        "description": "A factual detail about the user, environment, resource, or working context.",
        "default_security_level": "restricted",
    },
    MemoryType.PLAN: {
        "description": "A plan, intended next step, or known future direction.",
        "default_security_level": "restricted",
    },
    MemoryType.DECISION: {
        "description": "A decision that should guide future work.",
        "default_security_level": "restricted",
    },
    MemoryType.RESOURCE: {
        "description": "A relevant tool, service, repo, device, document, account, or other named resource.",
        "default_security_level": "confidential",
    },
    MemoryType.CREDENTIAL_REFERENCE: {
        "description": "A safe pointer to a credential stored outside normal memory text.",
        "default_security_level": "restricted",
    },
}
