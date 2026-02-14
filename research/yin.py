import matplotlib.pyplot as plt
import librosa
import librosa.display
import numpy as np

y, sr = librosa.load("research/sounds/il tornitore.mp3", sr=None, mono=True)
hop_length = 512
f0, _, _ = librosa.pyin(y, fmin=80, fmax=2000, sr=sr, hop_length=hop_length)
times_f0 = librosa.frames_to_time(
    np.arange(len(f0)), sr=sr, hop_length=hop_length)
D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
fig, ax = plt.subplots()
img = librosa.display.specshow(D, x_axis='time', y_axis='log', ax=ax)
ax.set(title='pYIN fundamental frequency estimation')
fig.colorbar(img, ax=ax, format="%+2.f dB")
ax.plot(times_f0, f0, label='f0', color='cyan', linewidth=3)
ax.legend(loc='upper right')
plt.show()
