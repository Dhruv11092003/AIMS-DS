import os
from uuid import uuid4
from moviepy import VideoFileClip

AUDIO_OUTPUT_DIR = "storage/audios"


def extract_audio_from_video(video_path: str) -> str:
    """
    Extract audio from video using MoviePy (Python-only)
    """
    os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True)

    audio_filename = f"{uuid4()}.wav"
    audio_path = os.path.join(AUDIO_OUTPUT_DIR, audio_filename)

    video = VideoFileClip(video_path)

    if video.audio is None:
        video.close()
        raise ValueError("No audio track found in video")

    video.audio.write_audiofile(
        audio_path,
        fps=16000,
        nbytes=2,
        codec="pcm_s16le",
        logger=None
    )

    video.close()
    return audio_path
