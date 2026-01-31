import * as Tone from 'tone';

const DEFAULT_FFT_SIZE = 1024;

interface Config {
	audioUrl: string;
	loop?: boolean;
}

export class AudioAnalyzer {
	private player: Tone.Player;
	private fft: Tone.FFT;

	constructor(private config: Config) {
		this.player = new Tone.Player();
		this.player.loop = this.config.loop ?? false;
		this.fft = new Tone.FFT({
			size: DEFAULT_FFT_SIZE,
			smoothing: 0.8,
			normalRange: true
		});
		this.player.connect(this.fft);
		this.fft.toDestination();
		this.player.load(this.config.audioUrl);
	}

	assertReady() {
		if (!this.player.loaded) {
			throw new Error('Audio analyzer is not ready');
		}
	}

	startAudioContext() {
		return Tone.start();
	}

	start() {
		this.assertReady();
		this.player.start();
	}

	stop() {
		this.player.stop();
	}

	dispose() {
		this.player.dispose();
		this.fft.dispose();
	}
}
