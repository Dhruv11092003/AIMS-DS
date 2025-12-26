from app.services.scoring.confidence_score import (
    compute_audio_confidence,
    compute_text_confidence,
    compute_mcq_confidence
)


def compute_overall_confidence(audio_features, text_features, mcq_score):
    audio_conf = compute_audio_confidence(audio_features)
    text_conf = compute_text_confidence(text_features)
    mcq_conf = compute_mcq_confidence(mcq_score)

    # Weights (sum to 1)
    w_audio = 0.4
    w_text = 0.3
    w_mcq = 0.3

    overall = round(
        (w_audio * audio_conf) +
        (w_text * text_conf) +
        (w_mcq * mcq_conf),
        2
    )

    if overall >= 0.75:
        level = "high"
    elif overall >= 0.5:
        level = "medium"
    else:
        level = "low"

    return {
        "audio_confidence": audio_conf,
        "text_confidence": text_conf,
        "mcq_confidence": mcq_conf,
        "overall_confidence": overall,
        "confidence_level": level
    }
