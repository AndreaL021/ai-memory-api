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
