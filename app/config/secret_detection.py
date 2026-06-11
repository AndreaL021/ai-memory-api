import re


REDACTION_TEXT = "[REDACTED_SECRET]"

SECRET_PATTERNS = {
    # Matches .env-style assignments whose key name suggests a secret, for example:
    # OPENAI_API_KEY=sk-..., MY_SERVICE_TOKEN="...", or DB_PASSWORD=...
    #
    # (?i) makes the pattern case-insensitive.
    # \b[A-Z0-9_]* allows optional prefixes before the secret keyword.
    # (?:api[_-]?key|token|secret|password) requires a secret-related keyword.
    # \s*[:=]\s* accepts KEY=value and KEY: value formats.
    # ['\"]? accepts optional single/double quotes before the value.
    # ([A-Za-z0-9_\-./=+]{12,}) captures only the secret value, not the key name.
    "generic_api_key_assignment": re.compile(
        r"(?i)\b[A-Z0-9_]*(?:api[_-]?key|token|secret|password)[A-Z0-9_]*\s*[:=]\s*['\"]?([A-Za-z0-9_\-./=+]{12,})"
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
