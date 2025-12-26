import librosa
import numpy as np
from typing import Dict


def extract_audio_features(audio_path: str) -> Dict[str, float]:
    """
    Extract basic, explainable audio features for screening
    """
    # Load audio (mono, 16kHz)
    y, sr = librosa.load(audio_path, sr=16000, mono=True)

    duration = librosa.get_duration(y=y, sr=sr)

    # Root Mean Square (energy)
    rms = librosa.feature.rms(y=y)[0]
    avg_energy = float(np.mean(rms))

    # Silence vs speech (simple threshold)
    energy_threshold = np.percentile(rms, 25)
    speech_frames = rms > energy_threshold
    silence_frames = rms <= energy_threshold

    pause_ratio = float(np.sum(silence_frames) / len(rms))

    # Speech rate proxy
    speech_rate = float(np.sum(speech_frames) / duration)

    return {
        "duration_sec": round(duration, 2),
        "avg_energy": round(avg_energy, 6),
        "pause_ratio": round(pause_ratio, 3),
        "speech_rate_proxy": round(speech_rate, 2)
    }
