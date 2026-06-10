import re
from dataclasses import dataclass

from detect_secrets.core.scan import scan_line
from detect_secrets.settings import transient_settings


REDACTION_TEXT = "[REDACTED_SECRET]"


@dataclass(frozen=True)
class SecretMatch:
    secret_type: str
    start: int
    end: int


SECRET_PATTERNS = {
    "openai_api_key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "github_token": re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    "generic_api_key_assignment": re.compile(
        r"(?i)\b(api[_-]?key|token|secret|password)\s*[:=]\s*['\"]?([A-Za-z0-9_\-./=+]{12,})"
    ),
    "private_key": re.compile(
        r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----[\s\S]*?-----END (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"
    ),
}

DETECT_SECRETS_PLUGINS = [
    {"name": "ArtifactoryDetector"},
    {"name": "AWSKeyDetector"},
    {"name": "AzureStorageKeyDetector"},
    {"name": "BasicAuthDetector"},
    {"name": "CloudantDetector"},
    {"name": "DiscordBotTokenDetector"},
    {"name": "GitHubTokenDetector"},
    {"name": "GitLabTokenDetector"},
    {"name": "IbmCloudIamDetector"},
    {"name": "IbmCosHmacDetector"},
    {"name": "JwtTokenDetector"},
    {"name": "KeywordDetector"},
    {"name": "MailchimpDetector"},
    {"name": "NpmDetector"},
    {"name": "OpenAIDetector"},
    {"name": "PrivateKeyDetector"},
    {"name": "PypiTokenDetector"},
    {"name": "SendGridDetector"},
    {"name": "SlackDetector"},
    {"name": "SoftlayerDetector"},
    {"name": "SquareOAuthDetector"},
    {"name": "StripeDetector"},
    {"name": "TelegramBotTokenDetector"},
    {"name": "TwilioKeyDetector"},
]


def detect_secrets(text: str | None):
    """Find secret-like spans in text using detect-secrets plus local rules."""
    if not text:
        return []

    matches = []
    matches.extend(detect_secrets_with_library(text))

    for secret_type, pattern in SECRET_PATTERNS.items():
        for match in pattern.finditer(text):
            start, end = get_secret_value_span(secret_type, match)
            matches.append(
                SecretMatch(
                    secret_type=secret_type,
                    start=start,
                    end=end,
                )
            )

    return merge_overlapping_matches(matches)


def detect_secrets_with_library(text: str):
    """Run detect-secrets on chat/runtime text and return character spans."""
    matches = []
    line_start = 0

    # Entropy plugins are intentionally excluded from DETECT_SECRETS_PLUGINS:
    # they are useful for repository scans but too noisy for natural chat text.
    with transient_settings({"plugins_used": DETECT_SECRETS_PLUGINS}):
        for line in text.splitlines(keepends=True):
            line_without_newline = line.rstrip("\r\n")

            for secret in scan_line(line_without_newline):
                if not secret.secret_value:
                    continue

                value_start = line_without_newline.find(secret.secret_value)

                if value_start == -1:
                    continue

                start = line_start + value_start
                end = start + len(secret.secret_value)
                matches.append(
                    SecretMatch(
                        secret_type=normalize_secret_type(secret.type),
                        start=start,
                        end=end,
                    )
                )

            line_start += len(line)

    return matches


def normalize_secret_type(secret_type: str):
    """Convert detect-secrets detector names into stable snake_case labels."""
    return re.sub(
        r"[^a-z0-9]+",
        "_",
        secret_type.lower(),
    ).strip("_")


def get_secret_value_span(secret_type: str, match: re.Match):
    """Return only the sensitive value span when a rule matches an assignment."""
    if secret_type == "generic_api_key_assignment" and match.lastindex and match.lastindex >= 2:
        return match.start(2), match.end(2)

    return match.start(), match.end()


def merge_overlapping_matches(matches: list[SecretMatch]):
    # Merge overlapping detections so redaction does not corrupt the text.
    if not matches:
        return []

    sorted_matches = sorted(
        matches,
        key=lambda item: (item.start, item.end),
    )
    merged = [sorted_matches[0]]

    for item in sorted_matches[1:]:
        previous = merged[-1]

        if item.start <= previous.end:
            merged[-1] = SecretMatch(
                secret_type=previous.secret_type,
                start=previous.start,
                end=max(previous.end, item.end),
            )
            continue

        merged.append(item)

    return merged


def redact_secrets(text: str | None):
    # Replace detected secret values with a safe placeholder.
    if not text:
        return text

    matches = detect_secrets(text)

    if not matches:
        return text

    redacted_parts = []
    cursor = 0

    for match in matches:
        redacted_parts.append(text[cursor:match.start])
        redacted_parts.append(REDACTION_TEXT)
        cursor = match.end

    redacted_parts.append(text[cursor:])
    return "".join(redacted_parts)
