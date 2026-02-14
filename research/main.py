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
audio_path = "research/sounds/i colori dell_acciaio.mp3"  # <-- change to your file
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


# def add_visualizer_feature_overlays(ax, y, sr, hop_length=512):
#     """
#     Draws multiple perceptual audio features aligned to spectrogram time.
#     Returns dictionary of computed features (optional future use).
#     """

#     # ---------- helper ----------
#     def normalize(x):
#         x = np.nan_to_num(x)
#         return (x - x.min()) / (x.max() - x.min() + 1e-8)

#     def smooth(x, w=9):
#         return np.convolve(x, np.ones(w)/w, mode="same")

#     # ---------- features ----------
#     times = librosa.times_like(librosa.stft(
#         y, hop_length=hop_length), sr=sr, hop_length=hop_length)

#     # Loudness
#     rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]

#     # Activity (spectral flux)
#     flux = librosa.onset.onset_strength(y=y, sr=sr)

#     # Pitch (melody position)
#     f0, _, _ = librosa.pyin(y, fmin=80, fmax=2000,
#                             sr=sr, hop_length=hop_length)
#     f0 = np.nan_to_num(f0)

#     # Timbre (shape identity)
#     mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=5, hop_length=hop_length)

#     # Brightness (color)
#     centroid = librosa.feature.spectral_centroid(
#         y=y, sr=sr, hop_length=hop_length)[0]

#     # ---------- normalize ----------
#     rms = smooth(normalize(rms))
#     flux = smooth(normalize(flux))
#     f0 = smooth(normalize(f0))
#     centroid = smooth(normalize(centroid))

#     mfcc = [smooth(normalize(m)) for m in mfcc]

#     # ---------- vertical layout ----------
#     # each feature gets its own horizontal lane over spectrogram
#     base = ax.get_ylim()[1]
#     height = base * 0.18

#     def lane(ydata, offset):
#         return ydata * height + offset

#     offsets = [
#         base * 0.82,  # RMS
#         base * 0.64,  # Flux
#         base * 0.46,  # Pitch
#         base * 0.28,  # Centroid
#         base * 0.10   # MFCC
#     ]

#     # ---------- plotting ----------
#     ax.plot(times, lane(rms, offsets[0]),
#             color="white", linewidth=1.6, label="Loudness")
#     ax.plot(times, lane(flux, offsets[1]),
#             color="orange", linewidth=1.4, label="Activity")
#     ax.plot(times, lane(f0, offsets[2]),
#             color="cyan", linewidth=1.4, label="Pitch")
#     ax.plot(times, lane(
#         centroid, offsets[3]), color="lime", linewidth=1.4, label="Brightness")

#     # MFCC combined curve (timbre identity)
#     mfcc_mix = np.mean(mfcc[1:4], axis=0)
#     ax.plot(times, lane(mfcc_mix, offsets[4]),
#             color="magenta", linewidth=1.2, label="Timbre")

#     ax.legend(loc="lower left", fontsize=8)

#     return {
#         "times": times,
#         "rms": rms,
#         "flux": flux,
#         "f0": f0,
#         "centroid": centroid,
#         "mfcc": mfcc_mix
#     }

def detect_offsets(y, sr, onsets, hop_length=512, drop_ratio=0.25):
    rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]
    times = librosa.frames_to_time(
        np.arange(len(rms)), sr=sr, hop_length=hop_length)

    offsets = []

    for onset in onsets:
        idx = np.searchsorted(times, onset)

        peak = rms[idx]
        threshold = peak * drop_ratio

        # move forward until energy falls below threshold
        for i in range(idx, len(rms)):
            if rms[i] < threshold:
                offsets.append(times[i])
                break
        else:
            offsets.append(times[-1])

    return np.array(offsets)


# features = add_visualizer_feature_overlays(ax, y, sr, hop_length)

ax.set_title("Spectrogram with Onsets & Spectral Centroid")

# Onset lines
for onset in onset_times:
    ax.axvline(onset, color='cyan', alpha=0.6, linewidth=1)

offset_times = detect_offsets(y, sr, onset_times)
for off in offset_times:
    ax.axvline(off, color='red', alpha=0.4, linewidth=1)

#


def onset_main_frequencies(y, sr, onset_times, n_fft=2048, hop_length=512):
    """
    Returns dominant frequency (Hz) at each onset
    """

    # Spectrogram magnitude
    S = np.abs(librosa.stft(y, n_fft=n_fft, hop_length=hop_length))
    freqs = librosa.fft_frequencies(sr=sr, n_fft=n_fft)
    times = librosa.frames_to_time(
        np.arange(S.shape[1]), sr=sr, hop_length=hop_length)

    onset_freqs = []

    for onset in onset_times:
        frame = np.argmin(np.abs(times - onset))
        spectrum = S[:, frame]

        # Ignore very low rumble
        spectrum[freqs < 50] = 0

        peak_bin = np.argmax(spectrum)
        onset_freqs.append(freqs[peak_bin])

    return np.array(onset_freqs)


onset_freqs = onset_main_frequencies(y, sr, onset_times)
for t, f in zip(onset_times, onset_freqs):
    ax.scatter(t, f, color='yellow', s=35, edgecolor='black', zorder=5)


def offset_main_frequencies(y, sr, offset_times, n_fft=2048, hop_length=512):
    """
    Returns dominant frequency (Hz) near each offset
    """

    S = np.abs(librosa.stft(y, n_fft=n_fft, hop_length=hop_length))
    freqs = librosa.fft_frequencies(sr=sr, n_fft=n_fft)
    times = librosa.frames_to_time(
        np.arange(S.shape[1]), sr=sr, hop_length=hop_length)

    offset_freqs = []

    for off in offset_times:
        frame = np.argmin(np.abs(times - off))
        spectrum = S[:, frame]

        # remove rumble
        spectrum[freqs < 50] = 0

        peak_bin = np.argmax(spectrum)
        offset_freqs.append(freqs[peak_bin])

    return np.array(offset_freqs)


offset_freqs = offset_main_frequencies(y, sr, offset_times)
for t, f in zip(offset_times, offset_freqs):
    ax.scatter(t, f, color='green', s=35, edgecolor='black', zorder=5)


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
        paused_position = stream_start_position + \
            (time.perf_counter() - stream_start_time)


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
