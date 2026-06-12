import re
from dataclasses import dataclass

from rapidfuzz import fuzz
from sqlalchemy.orm import Session

from app.config.memory_capture import (
    AUTO_PROMOTE_CONFIDENCE,
    CANDIDATE_MAX_CONFIDENCE,
    CANDIDATE_MIN_SCORE,
    FUZZY_MATCH_THRESHOLD,
    KEYWORD_MATCH_SCORE,
    MEMORY_TYPE_SIGNALS,
    PHRASE_MATCH_SCORE,
)
from app.models.event_model import EventModel
from app.models.memory_candidate_model import MemoryCandidateModel
from app.models.memory_model import MemoryModel
from app.schemas.memory_schema import MemoryCreateSchema
from app.services.memory.audit_service import create_memory_log
from app.services.memory.memory_service import create_memory


@dataclass(frozen=True)
class CandidateDraft:
    memory_type: str
    content: str
    confidence: int
    reason: str
    signals: dict


def process_event_for_memory_candidates(
    db: Session,
    event: EventModel,
):
    # Create memory candidates from one stored event and record why they were created.
    drafts = extract_memory_candidate_drafts(event.content)
    candidates = []

    for draft in drafts:
        candidate = MemoryCandidateModel(
            id_event=event.id,
            id_user=event.id_user,
            memory_type=draft.memory_type,
            content=draft.content,
            confidence=draft.confidence,
            reason=draft.reason,
            status="accepted" if draft.confidence >= AUTO_PROMOTE_CONFIDENCE else "pending",
            signals=draft.signals,
        )
        db.add(candidate)
        db.flush()
        create_memory_log(
            db=db,
            id_user=event.id_user,
            id_event=event.id,
            action="memory_candidate_created",
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
    # Return one memory candidate by id, or None when it does not exist.
    return (
        db.query(MemoryCandidateModel)
        .filter(MemoryCandidateModel.id == candidate_id)
        .first()
    )


def promote_memory_candidate(db: Session, candidate: MemoryCandidateModel):
    # Convert a candidate into a persistent memory, avoiding duplicate promotion.
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
            id_event=candidate.id_event,
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
    create_memory_log(
        db=db,
        id_user=candidate.id_user,
        id_event=candidate.id_event,
        id_memory=memory.id,
        action="memory_candidate_promoted",
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
    # Split input text, score each part, and return draft memories worth reviewing.
    drafts = []

    for sentence in split_candidate_sentences(text):
        scored_types = [
            score_memory_type(sentence, memory_type, config)
            for memory_type, config in MEMORY_TYPE_SIGNALS.items()
        ]
        scored_types = [
            item
            for item in scored_types
            if item["score"] >= CANDIDATE_MIN_SCORE
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
                # \s+ matches any run of whitespace, including spaces, tabs, and newlines.
                # Replacing it with one normal space keeps the original wording readable.
                content=re.sub(r"\s+", " ", sentence).strip(),
                confidence=min(CANDIDATE_MAX_CONFIDENCE, best["score"]),
                reason=f"Matched {best['memory_type']} signals: {', '.join(best['matched_signals'])}",
                signals={
                    "matched_signals": best["matched_signals"],
                    "score": best["score"],
                },
            )
        )

    return deduplicate_candidate_drafts(drafts)


def split_candidate_sentences(text: str):
    # Break chat text into candidate-sized pieces while keeping short notes usable.
    return [
        item.strip(" -\t.")
        # [\n!?]+ splits on newlines, question marks, and exclamation marks.
        # (?<=\.)\s+ splits after a period only when it is followed by whitespace,
        # so filenames like quality_cases.json are not split into separate candidates.
        for item in re.split(r"[\n!?]+|(?<=\.)\s+", text)
        if item.strip(" -\t.")
    ]


def score_memory_type(sentence: str, memory_type: str, config: dict):
    # Score one sentence against the phrase and keyword signals for one memory type.
    normalized_sentence = sentence.lower()
    matched_signals = []
    score = 0

    for phrase in config["phrases"]:
        phrase_score = fuzz.partial_ratio(phrase, normalized_sentence)

        if phrase_score >= FUZZY_MATCH_THRESHOLD:
            matched_signals.append(phrase)
            score += PHRASE_MATCH_SCORE

    # \b marks word boundaries, the character class accepts letters, numbers,
    # underscores, and hyphens, and {3,} ignores very short words like "to".
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
            score += KEYWORD_MATCH_SCORE

    return {
        "memory_type": memory_type,
        "score": min(score, CANDIDATE_MAX_CONFIDENCE),
        "matched_signals": sorted(set(matched_signals)),
    }




def deduplicate_candidate_drafts(drafts: list[CandidateDraft]):
    # Remove duplicate draft memories with the same type and normalized content.
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
