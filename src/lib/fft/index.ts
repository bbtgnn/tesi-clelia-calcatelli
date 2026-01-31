import * as Tone from 'tone';

const DEFAULT_FFT_SIZE = 1024;

export interface LoadAndAnalyzeOptions {
	/** FFT size (power of two, 16–16384). Default 1024. */
	fftSize?: number;
	/** Smoothing (0 = no averaging). Default 0.8. */
	smoothing?: number;
	/** If true, FFT values are normalized to 0–1. Default true. */
	normalRange?: boolean;
	/** If true, the audio loops. Default false. */
	loop?: boolean;
}

export interface AudioAnalyzer {
	/** Start playback (from beginning or current position). */
	play: (offset?: number) => void;
	/** Stop playback. */
	stop: () => void;
	/** Get current FFT frequency data (Float32Array of decibel or 0–1 values). */
	getFFTData: () => Float32Array;
	/** Get frequency in Hz for a given FFT bin index. */
	getFrequencyOfIndex: (index: number) => number;
	/** Number of FFT bins (same as fftSize). */
	readonly fftSize: number;
	/** Whether the buffer is loaded and ready. */
	readonly loaded: boolean;
	/** Dispose player and FFT (free resources). */
	dispose: () => void;
}

/**
 * Load an audio file from a URL, then play it and analyze its FFT with Tone.js.
 * Must be called after a user gesture (e.g. click); the first call will start the audio context.
 *
 * @param url - URL of the audio file (e.g. MP3, WAV, OGG).
 * @param options - Optional FFT and analysis settings.
 * @returns Promise resolving to an AudioAnalyzer with play, stop, getFFTData, etc.
 */
export async function loadPlayAndAnalyze(
	url: string,
	options: LoadAndAnalyzeOptions = {}
): Promise<AudioAnalyzer> {
	// Start the audio context (required after user gesture in browsers)
	await Tone.start();

	const {
		fftSize = DEFAULT_FFT_SIZE,
		smoothing = 0.8,
		normalRange = true,
		loop = false
	} = options;

	const player = new Tone.Player();
	const fft = new Tone.FFT({
		size: fftSize,
		smoothing,
		normalRange
	});

	// Route: player -> fft -> destination (so we hear and analyze)
	player.connect(fft);
	fft.toDestination();

	await player.load(url);
	player.loop = loop;

	const analyzer: AudioAnalyzer = {
		play: (offset?: number) => {
			player.start(undefined, offset);
		},
		stop: () => {
			player.stop();
		},
		getFFTData: () => fft.getValue(),
		getFrequencyOfIndex: (index: number) => fft.getFrequencyOfIndex(index),
		get fftSize() {
			return fft.size;
		},
		get loaded() {
			return player.loaded;
		},
		dispose: () => {
			player.dispose();
			fft.dispose();
		}
	};

	return analyzer;
}
