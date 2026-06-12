CANDIDATE_CASES = [
    {
        "name": "Preference input creates high-confidence candidate",
        "input": "I prefer short answers in Italian.",
        "expected_count": 1,
        "expected_types": ["preference"],
        "expected_promotable": True,
    },
    {
        "name": "Decision input creates decision candidate",
        "input": "We decided to use PostgreSQL.",
        "expected_count": 1,
        "expected_types": ["decision"],
    },
    {
        "name": "Resource input with typo creates candidate",
        "input": "Im using Postgres for this project.",
        "expected_count": 1,
        "expected_types": ["resource"],
    },
    {
        "name": "Generic chat does not create candidate",
        "input": "Hello, can you help me?",
        "expected_count": 0,
        "expected_types": [],
    },
    {
        "name": "Preference and decision in one message create two candidates",
        "input": "I prefeer concise replies. We decidded to use PostgreSQL.",
        "expected_count": 2,
        "expected_types": ["preference", "decision"],
    },
    {
        "name": "Plan and resource in one message create two candidates",
        "input": "Next step is to add memory logs. Im using pgAdmin to inspect the database.",
        "expected_count": 2,
        "expected_types": ["plan", "resource"],
    },
    {
        "name": "Method and failure note create reusable method candidate",
        "input": "Last time Docker failed, it worked by restarting WSLService.",
        "expected_count": 1,
        "expected_types": ["method"],
    },
    {
        "name": "Resource fact with typo still creates candidate",
        "input": "The repo is caled ai-memory-api and runs on port 8000.",
        "expected_count": 1,
        "expected_types": ["resource"],
    },
    {
        "name": "Secret plus safe resource creates only safe candidate",
        "input": "OPENAI_API_KEY=sk-testsecretvalue1234567890. Im using Postgres for local memory storage.",
        "expected_count": 1,
        "expected_types": ["resource"],
    },
]

SECRET_CASES = [
    {
        "name": "Secret input is redacted and blocked",
        "input": "OPENAI_API_KEY=sk-testsecretvalue1234567890",
        "expected_can_store": False,
        "expected_security_level": "blocked_secret",
        "expected_redacted": True,
        "forbidden_text": "sk-testsecretvalue1234567890",
    },
]
