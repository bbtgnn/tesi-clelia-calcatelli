import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display
import sounddevice as sd
import time
from matplotlib.animation import FuncAnimation

# ======================
# 1. Load audio
# ======================
audio_path = "research/sounds/il laminatore.mp3"  # <-- change to your file
y, sr = librosa.load(audio_path, sr=None, mono=True)

duration = len(y) / sr

# ======================
# 2. Spectrogram
# ======================
n_fft = 2048
hop_length = 512

S = np.abs(librosa.stft(y, n_fft=n_fft, hop_length=hop_length))
S_db = librosa.amplitude_to_db(S, ref=np.max)

# Time axis for frames
times = librosa.times_like(S, sr=sr, hop_length=hop_length)

# ======================
# 3. Onset detection
# ======================
onset_frames = librosa.onset.onset_detect(y=y, sr=sr, hop_length=hop_length)
onset_times = librosa.frames_to_time(
    onset_frames, sr=sr, hop_length=hop_length)

# ======================
# 4. Spectral centroid
# ======================
centroid = librosa.feature.spectral_centroid(
    y=y, sr=sr, hop_length=hop_length)[0]

# ======================
# 5. Plot setup
# ======================
fig, ax = plt.subplots(figsize=(12, 6))

# Spectrogram
img = librosa.display.specshow(
    S_db,
    sr=sr,
    hop_length=hop_length,
    x_axis="time",
    y_axis="log",
    cmap="magma",
    ax=ax
)

ax.set_title("Spectrogram with Onsets & Spectral Centroid")

# Onset lines
for onset in onset_times:
    ax.axvline(onset, color='cyan', alpha=0.6, linewidth=1)

# Spectral centroid curve
centroid_line, = ax.plot(times, centroid, color='lime',
                         linewidth=2, label="Spectral Centroid")
ax.legend(loc="upper right")

# Playhead line
playhead = ax.axvline(0, color='white', linewidth=2)

plt.tight_layout()

# ======================
# 6. Audio playback (loop + play/pause)
# ======================
stream_start_time = None
stream_start_position = 0.0
paused = False
paused_position = 0.0


def play_from(position=0.0):
    global stream_start_time, stream_start_position, paused
    paused = False
    stream_start_position = position
    stream_start_time = time.perf_counter()
    start_sample = int(position * sr)
    sd.play(y[start_sample:], sr, blocking=False)


def pause_playback():
    global paused, paused_position, stream_start_time, stream_start_position
    sd.stop()
    paused = True
    if stream_start_time is not None:
        paused_position = stream_start_position + (time.perf_counter() - stream_start_time)


def get_elapsed():
    if paused:
        return paused_position
    if stream_start_time is not None:
        return stream_start_position + (time.perf_counter() - stream_start_time)
    return 0.0


def on_key(event):
    global paused
    if event.key != " ":
        return
    if paused:
        play_from(paused_position)
    else:
        pause_playback()


fig.canvas.mpl_connect("key_press_event", on_key)

# ======================
# 7. Animation update
# ======================


def update(frame):
    if stream_start_time is None and not paused:
        return playhead,

    elapsed = get_elapsed()
    # Loop when we reach the end (only when playing)
    if not paused and elapsed >= duration:
        play_from(0.0)
        elapsed = 0.0

    playhead.set_xdata([elapsed, elapsed])
    return playhead,


ani = FuncAnimation(fig, update, interval=30, blit=True)

# Start playback when window appears
plt.pause(0.1)
play_from(0.0)

plt.show()

sd.stop()
