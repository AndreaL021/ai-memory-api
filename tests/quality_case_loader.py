import json
from pathlib import Path


QUALITY_CASES_PATH = Path(__file__).with_name("quality_cases.json")


def load_quality_cases():
    # Load the editable quality dataset used by unittest and the readable report.
    return json.loads(QUALITY_CASES_PATH.read_text(encoding="utf-8"))
