import * as Tone from 'tone';

//

const DEFAULT_FFT_SIZE = 1024;

export interface Config {
	audioUrl: string;
	barCount: number;
	loop?: boolean;
}

export interface Result {
	bars: BarData[];
	highestBar: number;
}

export interface BarData {
	frequency: number;
	value: number;
}

export class Analyzer {
	private player: Tone.Player;
	private fft: Tone.FFT;

	private barCount = 20;
	private ready = false;

	constructor() {
		this.player = new Tone.Player();
		this.fft = new Tone.FFT({
			size: DEFAULT_FFT_SIZE,
			smoothing: 0.8,
			normalRange: true
		});
		this.player.connect(this.fft);
		this.fft.toDestination();
	}

	setConfig(config: Config) {
		this.ready = false;
		this.barCount = config.barCount;
		this.player.loop = config.loop ?? true;
		this.player.load(config.audioUrl).then(() => {
			this.ready = true;
		});
	}

	assertReady() {
		if (this.ready) return;
		throw new Error('Audio analyzer is not ready');
	}

	async start() {
		this.assertReady();
		await Tone.start();
		this.player.start();
	}

	stop() {
		this.player.stop();
	}

	dispose() {
		this.player.dispose();
		this.fft.dispose();
	}

	analyze(): Result {
		const fftData = this.fft.getValue();
		const bars = convertFFTToBarData(fftData, this.barCount, (index) =>
			this.fft.getFrequencyOfIndex(index)
		);
		const highestBar = bars.findIndex((b) => b.value === Math.max(...bars.map((b) => b.value)));
		return { bars, highestBar };
	}
}

function convertFFTToBarData(
	fftData: Float32Array,
	numBars: number,
	getFrequencyOfIndex: (binIndex: number) => Tone.Unit.Hertz
): BarData[] {
	const numBins = fftData.length;
	const binsPerBar = Math.max(1, Math.floor(numBins / numBars));
	const bars: BarData[] = [];
	for (let i = 0; i < numBars; i++) {
		let sum = 0;
		for (let j = 0; j < binsPerBar; j++) {
			sum += fftData[i * binsPerBar + j] ?? 0;
		}
		bars.push({
			frequency: getFrequencyOfIndex(i * binsPerBar + Math.floor(binsPerBar / 2)),
			value: sum / binsPerBar
		});
	}
	const max = Math.max(...bars.map((b) => b.value), 1e-9);
	return bars.map((b) => ({ ...b, value: b.value / max }));
}
