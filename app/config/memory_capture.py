AUTO_PROMOTE_CONFIDENCE = 85
FUZZY_MATCH_THRESHOLD = 86
CANDIDATE_MIN_SCORE = 55
CANDIDATE_MAX_CONFIDENCE = 95
PHRASE_MATCH_SCORE = 35
KEYWORD_MATCH_SCORE = 12

MEMORY_TYPE_SIGNALS = {
    "preference": {
        "phrases": [
            "i prefer",
            "i like",
            "i want",
            "please always",
            "do not",
            "don't",
            "from now on",
        ],
        "keywords": [
            "answer",
            "answers",
            "italian",
            "prefer",
            "reply",
            "replies",
            "short",
            "style",
            "format",
            "language",
            "concise",
            "verbose",
        ],
    },
    "decision": {
        "phrases": [
            "we decided",
            "i decided",
            "decision",
            "we will use",
            "we won't use",
            "let's use",
        ],
        "keywords": [
            "decided",
            "choice",
            "selected",
            "approved",
        ],
    },
    "plan": {
        "phrases": [
            "next step",
            "todo",
            "we need to",
            "i will",
            "plan",
            "later we",
        ],
        "keywords": [
            "next",
            "todo",
            "plan",
            "later",
            "tomorrow",
        ],
    },
    "method": {
        "phrases": [
            "to fix",
            "the way to",
            "last time",
            "steps",
            "worked by",
            "solved by",
        ],
        "keywords": [
            "fix",
            "solved",
            "worked",
            "failed",
            "steps",
        ],
    },
    "resource": {
        "phrases": [
            "repo is",
            "repository is",
            "we use",
            "tool is",
            "runs on",
            "api is",
        ],
        "keywords": [
            "repo",
            "repository",
            "tool",
            "api",
            "service",
            "port",
        ],
    },
    "fact": {
        "phrases": [
            "is called",
            "is named",
            "uses",
            "runs on",
            "is located",
        ],
        "keywords": [
            "uses",
            "called",
            "named",
            "located",
        ],
    },
}
