def compute_audio_confidence(audio_features: dict) -> float:
    """
    Compute confidence from audio behavior (0–1)
    """

    duration = audio_features.get("duration_sec", 0)
    pause_ratio = audio_features.get("pause_ratio", 1)
    speech_rate = audio_features.get("speech_rate_proxy", 0)

    score = 1.0

    # Penalize very short answers
    if duration < 5:
        score -= 0.3
    elif duration < 8:
        score -= 0.15

    # Penalize excessive pauses
    if pause_ratio > 0.6:
        score -= 0.4
    elif pause_ratio > 0.4:
        score -= 0.2

    # Penalize very slow speech
    if speech_rate < 10:
        score -= 0.2

    return round(max(score, 0.0), 2)

def compute_text_confidence(text_features: dict) -> float:
    """
    Compute confidence from transcript structure (0–1)
    """

    word_count = text_features.get("word_count", 0)
    hesitation_ratio = text_features.get("hesitation_ratio", 0)

    score = 1.0

    # Penalize extremely short responses
    if word_count < 10:
        score -= 0.4
    elif word_count < 20:
        score -= 0.2

    # Penalize hesitation
    if hesitation_ratio > 0.3:
        score -= 0.3
    elif hesitation_ratio > 0.15:
        score -= 0.15

    return round(max(score, 0.0), 2)

def compute_mcq_confidence(mcq_score: int) -> float:
    """
    Compute confidence from MCQ consistency (0–1)
    """
    if mcq_score <= 3:
        return 0.9
    elif mcq_score <= 7:
        return 0.7
    elif mcq_score <= 11:
        return 0.7
    else:
        return 0.9
