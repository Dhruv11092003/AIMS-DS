import re
from typing import Dict

NEGATIVE_WORDS = {
    "sad", "tired", "hopeless", "empty", "lonely", "worthless",
    "anxious", "stress", "depressed", "low", "bad"
}

HESITATION_WORDS = {
    "uh", "um", "hmm", "erm", "ah"
}

FIRST_PERSON_PRONOUNS = {
    "i", "me", "my", "mine"
}


def extract_text_features(transcript: str) -> Dict[str, float]:
    text = transcript.lower()
    words = re.findall(r"\b\w+\b", text)

    word_count = len(words)

    sentences = re.split(r"[.!?]", transcript)
    sentences = [s for s in sentences if s.strip()]
    avg_sentence_length = (
        sum(len(s.split()) for s in sentences) / len(sentences)
        if sentences else 0
    )

    hesitation_count = sum(word in HESITATION_WORDS for word in words)
    negative_count = sum(word in NEGATIVE_WORDS for word in words)
    first_person_count = sum(word in FIRST_PERSON_PRONOUNS for word in words)

    return {
        "word_count": word_count,
        "avg_sentence_length": round(avg_sentence_length, 2),
        "hesitation_ratio": round(hesitation_count / max(word_count, 1), 3),
        "negative_word_ratio": round(negative_count / max(word_count, 1), 3),
        "first_person_ratio": round(first_person_count / max(word_count, 1), 3),
    }
