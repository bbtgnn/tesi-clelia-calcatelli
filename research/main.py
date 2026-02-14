"""Draw spectrogram of an audio file from src/lib/assets/sounds/."""

from pathlib import Path

import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np

# Path to sounds folder (relative to project root)
PROJECT_ROOT = Path(__file__).parent
SOUNDS_DIR = PROJECT_ROOT / "sounds"

# Pick an audio file (change this to use another file from the folder)
AUDIO_FILE = SOUNDS_DIR / "il tornitore.mp3"


def main() -> None:
    if not AUDIO_FILE.exists():
        raise FileNotFoundError(f"Audio file not found: {AUDIO_FILE}")

    # Load audio (mono, resampled to 22050 Hz for consistent spectrogram)
    y, sr = librosa.load(AUDIO_FILE, sr=22050, mono=True)

    # Compute mel spectrogram (log amplitude)
    mel_spec = librosa.feature.melspectrogram(
        y=y, sr=sr, n_mels=128, fmax=8000)
    mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)

    # Compute onset envelope and detect onsets
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    onsets = librosa.onset.onset_detect(
        onset_envelope=onset_env, sr=sr, backtrack=True
    )
    times = librosa.frames_to_time(onsets, sr=sr)

    # Plot
    fig, ax = plt.subplots(figsize=(12, 5))
    img = librosa.display.specshow(
        mel_spec_db,
        x_axis="time",
        y_axis="mel",
        sr=sr,
        fmax=8000,
        ax=ax,
        cmap="magma",
    )
    # Red vertical lines at each onset
    for t in times:
        ax.axvline(x=t, color="red", linewidth=1, alpha=0.9)
    fig.colorbar(img, ax=ax, format="%+2.0f dB")
    ax.set_title(f"Spectrogram: {AUDIO_FILE.name}")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
