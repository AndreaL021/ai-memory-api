from enum import Enum


class MemoryType(str, Enum):

    # What the user likes/wants.
    PREFERENCE = "preference"
    # How to do something, including fixes and lessons.
    METHOD = "method"
    # Something true about the user, project, context, or resource.
    FACT = "fact"
    # Something intended or scheduled.
    PLAN = "plan"
    # A choice already made.
    DECISION = "decision"
    # A thing used or referenced: repo, tool, API, device, file, service, account.
    RESOURCE = "resource"
    # Safe pointer to a securely stored credential.
    CREDENTIAL_REFERENCE = "credential_reference"


MEMORY_TYPE_DEFINITIONS = {
    MemoryType.PREFERENCE: {
        "description": "A user preference that should influence future behavior.",
        "default_security_level": "confidential",
        "project_scoped": False,
    },
    MemoryType.METHOD: {
        "description": "A reusable way of doing something, including workflows, fixes, and lessons learned.",
        "default_security_level": "confidential",
        "project_scoped": False,
    },
    MemoryType.FACT: {
        "description": "A factual detail about the user, project, environment, resource, or working context.",
        "default_security_level": "restricted",
        "project_scoped": True,
    },
    MemoryType.PLAN: {
        "description": "A plan, intended next step, or known future direction.",
        "default_security_level": "restricted",
        "project_scoped": True,
    },
    MemoryType.DECISION: {
        "description": "A decision that should guide future work.",
        "default_security_level": "restricted",
        "project_scoped": True,
    },
    MemoryType.RESOURCE: {
        "description": "A relevant tool, service, repo, device, document, account, or other named resource.",
        "default_security_level": "confidential",
        "project_scoped": False,
    },
    MemoryType.CREDENTIAL_REFERENCE: {
        "description": "A safe pointer to a credential stored outside normal memory text.",
        "default_security_level": "restricted",
        "project_scoped": True,
    },
}
