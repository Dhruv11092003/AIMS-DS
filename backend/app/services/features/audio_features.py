import librosa
import numpy as np


def extract_audio_features(audio_path: str) -> np.ndarray:
    """
    Extract audio features and return a numeric feature vector
    compatible with direct fusion.

    Output shape: (D,)
    """

    # Load audio (mono, 16kHz)
    y, sr = librosa.load(audio_path, sr=16000, mono=True)

    duration = librosa.get_duration(y=y, sr=sr)

    # Root Mean Square (energy)
    rms = librosa.feature.rms(y=y)[0]
    avg_energy = np.mean(rms)

    # Silence vs speech
    energy_threshold = np.percentile(rms, 25)
    speech_frames = rms > energy_threshold
    silence_frames = rms <= energy_threshold

    pause_ratio = np.sum(silence_frames) / len(rms)

    # Speech rate proxy
    speech_rate = np.sum(speech_frames) / max(duration, 1e-6)

    # ---- FINAL FEATURE VECTOR ----
    feature_vector = np.array(
        [
            duration,
            avg_energy,
            pause_ratio,
            speech_rate
        ],
        dtype=np.float32
    )

    return feature_vector
