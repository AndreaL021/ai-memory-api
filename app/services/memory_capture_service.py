import re
from dataclasses import dataclass

from rapidfuzz import fuzz
from sqlalchemy.orm import Session

from app.models.event_model import EventModel
from app.models.memory_candidate_model import MemoryCandidateModel
from app.models.memory_model import MemoryModel
from app.schemas.memory_schema import MemoryCreateSchema
from app.services.audit_service import create_memory_observation
from app.services.memory_service import create_memory


AUTO_PROMOTE_CONFIDENCE = 85
FUZZY_MATCH_THRESHOLD = 86

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


@dataclass(frozen=True)
class CandidateDraft:
    memory_type: str
    content: str
    confidence: int
    reason: str
    signals: dict


def process_event_for_memory_candidates(db: Session, event: EventModel):
    # Convert a captured event into observable memory candidates.
    drafts = extract_memory_candidate_drafts(event.content)
    candidates = []

    for draft in drafts:
        candidate = MemoryCandidateModel(
            id_event=event.id,
            id_user=event.id_user,
            id_project=event.id_project,
            memory_type=draft.memory_type,
            content=draft.content,
            confidence=draft.confidence,
            reason=draft.reason,
            status="accepted" if draft.confidence >= AUTO_PROMOTE_CONFIDENCE else "pending",
            signals=draft.signals,
        )
        db.add(candidate)
        db.flush()
        create_memory_observation(
            db=db,
            id_user=event.id_user,
            id_project=event.id_project,
            id_event=event.id,
            observation_type="memory_candidate_created",
            reason=draft.reason,
            decision=candidate.status,
            metrics={
                "candidate_id": candidate.id,
                "confidence": draft.confidence,
                "memory_type": draft.memory_type,
            },
        )
        candidates.append(candidate)

    event.processing_status = "processed"
    db.commit()

    for candidate in candidates:
        db.refresh(candidate)

    db.refresh(event)
    return candidates


def get_memory_candidate(db: Session, candidate_id: int):
    # Return a memory candidate by id, or None when it does not exist.
    return (
        db.query(MemoryCandidateModel)
        .filter(MemoryCandidateModel.id == candidate_id)
        .first()
    )


def promote_memory_candidate(db: Session, candidate: MemoryCandidateModel):
    # Turn an accepted/pending candidate into a stored memory record.
    if candidate.id_memory:
        return (
            db.query(MemoryModel)
            .filter(MemoryModel.id == candidate.id_memory)
            .first()
        )

    memory = create_memory(
        db=db,
        payload=MemoryCreateSchema(
            id_user=candidate.id_user,
            id_project=candidate.id_project,
            id_source_event=candidate.id_event,
            memory_type=candidate.memory_type,
            content=candidate.content,
            confidence=candidate.confidence,
            importance=candidate.confidence,
        ),
    )

    if not memory:
        candidate.status = "rejected"
        db.commit()
        return None

    candidate.id_memory = memory.id
    candidate.status = "promoted"
    create_memory_observation(
        db=db,
        id_user=candidate.id_user,
        id_project=candidate.id_project,
        id_event=candidate.id_event,
        id_memory=memory.id,
        observation_type="memory_candidate_promoted",
        reason="Memory candidate promoted to persistent memory.",
        decision="promoted",
        metrics={
            "candidate_id": candidate.id,
            "candidate_confidence": candidate.confidence,
            "memory_type": candidate.memory_type,
        },
    )
    db.commit()
    db.refresh(candidate)
    db.refresh(memory)
    return memory


def extract_memory_candidate_drafts(text: str):
    # Score each sentence against memory-type signals without using an LLM.
    drafts = []

    for sentence in split_candidate_sentences(text):
        scored_types = [
            score_memory_type(sentence, memory_type, config)
            for memory_type, config in MEMORY_TYPE_SIGNALS.items()
        ]
        scored_types = [
            item
            for item in scored_types
            if item["score"] >= 55
        ]

        if not scored_types:
            continue

        best = max(
            scored_types,
            key=lambda item: item["score"],
        )
        drafts.append(
            CandidateDraft(
                memory_type=best["memory_type"],
                content=normalize_candidate_content(sentence),
                confidence=min(95, best["score"]),
                reason=f"Matched {best['memory_type']} signals: {', '.join(best['matched_signals'])}",
                signals={
                    "matched_signals": best["matched_signals"],
                    "score": best["score"],
                },
            )
        )

    return deduplicate_candidate_drafts(drafts)


def split_candidate_sentences(text: str):
    # Keep line-based notes and sentence-based chat messages usable.
    return [
        item.strip(" -\t")
        for item in re.split(r"[\n.!?]+", text)
        if item.strip(" -\t")
    ]


def score_memory_type(sentence: str, memory_type: str, config: dict):
    normalized_sentence = sentence.lower()
    matched_signals = []
    score = 0

    for phrase in config["phrases"]:
        phrase_score = fuzz.partial_ratio(phrase, normalized_sentence)

        if phrase_score >= FUZZY_MATCH_THRESHOLD:
            matched_signals.append(phrase)
            score += 35

    words = set(re.findall(r"\b[a-zA-Z0-9_-]{3,}\b", normalized_sentence))

    for keyword in config["keywords"]:
        keyword_score = max(
            [
                fuzz.partial_ratio(keyword, word)
                for word in words
            ],
            default=0,
        )

        if keyword_score >= FUZZY_MATCH_THRESHOLD:
            matched_signals.append(keyword)
            score += 12

    return {
        "memory_type": memory_type,
        "score": min(score, 95),
        "matched_signals": sorted(set(matched_signals)),
    }


def normalize_candidate_content(sentence: str):
    # Keep user wording for traceability, but normalize whitespace.
    return re.sub(r"\s+", " ", sentence).strip()


def deduplicate_candidate_drafts(drafts: list[CandidateDraft]):
    unique_drafts = []
    seen = set()

    for draft in drafts:
        key = (
            draft.memory_type,
            draft.content.lower(),
        )

        if key in seen:
            continue

        seen.add(key)
        unique_drafts.append(draft)

    return unique_drafts
