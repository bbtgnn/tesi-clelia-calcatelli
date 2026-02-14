import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display
import sounddevice as sd
import time
from matplotlib.animation import FuncAnimation

# ==========================
# SETTINGS
# ==========================
audio_path = "research/sounds/il tornitore.mp3"
n_fft = 2048
hop_length = 512

# ==========================
# LOAD AUDIO
# ==========================
y, sr = librosa.load(audio_path, sr=None, mono=True)
duration = len(y) / sr

# ==========================
# SPECTROGRAM
# ==========================
S = np.abs(librosa.stft(y, n_fft=n_fft, hop_length=hop_length))
S_db = librosa.amplitude_to_db(S, ref=np.max)
times = librosa.times_like(S, sr=sr, hop_length=hop_length)

# ==========================
# ONSETS
# ==========================
onset_frames = librosa.onset.onset_detect(y=y, sr=sr, hop_length=hop_length)
onset_times = librosa.frames_to_time(
    onset_frames, sr=sr, hop_length=hop_length)

# ==========================
# OFFSETS via energy drop
# ==========================


def detect_offsets(y, sr, onset_times, hop_length=512, drop_ratio=0.25):
    rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]
    t = librosa.frames_to_time(
        np.arange(len(rms)), sr=sr, hop_length=hop_length)

    offsets = []
    for onset in onset_times:
        idx = np.searchsorted(t, onset)
        peak = rms[idx]
        thresh = peak * drop_ratio

        for i in range(idx, len(rms)):
            if rms[i] < thresh:
                offsets.append(t[i])
                break
        else:
            offsets.append(t[-1])
    return np.array(offsets)


offset_times = detect_offsets(y, sr, onset_times)

# ==========================
# PITCH TRACKING
# ==========================
f0, _, _ = librosa.pyin(y, fmin=80, fmax=2000, sr=sr, hop_length=hop_length)
pitch_times = librosa.times_like(f0, sr=sr, hop_length=hop_length)


def sample_pitch(query_times):
    vals = []
    for t in query_times:
        i = np.argmin(np.abs(pitch_times - t))
        vals.append(0 if np.isnan(f0[i]) else f0[i])
    return np.array(vals)


onset_freqs = sample_pitch(onset_times)
offset_freqs = sample_pitch(offset_times)

# ==========================
# CLASSIFY NOTES
# ==========================
notes = []
for t_on, t_off, f_on, f_off in zip(onset_times, offset_times, onset_freqs, offset_freqs):
    duration = t_off - t_on
    pitch = f_on if f_on > 0 else f_off

    if pitch == 0 or duration < 0.08:
        kind = "percussive"
    elif pitch < 180:
        kind = "bass"
    else:
        kind = "melody"

    notes.append((t_on, t_off, f_on, f_off, kind))

# ==========================
# PLOT
# ==========================
fig, ax = plt.subplots(figsize=(13, 6))

librosa.display.specshow(
    S_db,
    sr=sr,
    hop_length=hop_length,
    x_axis="time",
    y_axis="log",
    cmap="magma",
    ax=ax
)

ax.set_title("Musical Note Visualizer")

# draw notes
for t_on, t_off, f_on, f_off, kind in notes:
    if kind == "percussive":
        ax.axvline(t_on, color="white", alpha=0.7, linewidth=1)

    elif kind == "bass":
        ax.plot([t_on, t_off], [f_on, f_off], color="cyan", linewidth=4)

    else:  # melody
        ax.plot([t_on, t_off], [f_on, f_off], color="yellow", linewidth=2)

# playhead
playhead = ax.axvline(0, color='red', linewidth=2)

# ==========================
# AUDIO PLAYBACK
# ==========================
start_time = None


def start_audio():
    global start_time
    sd.play(y, sr, blocking=False)
    start_time = time.perf_counter()


def update(frame):
    if start_time is None:
        return playhead,

    elapsed = time.perf_counter() - start_time
    if elapsed > len(y)/sr:
        return playhead,

    playhead.set_xdata([elapsed, elapsed])
    return playhead,


ani = FuncAnimation(fig, update, interval=30,
                    blit=True, cache_frame_data=False)

plt.pause(0.1)
start_audio()
plt.show()
sd.stop()
