import type { JSAnimation } from 'animejs';

import * as AudioAnalyzer from '$lib/audio-analyzer';
import { Loop } from '$lib/utils/loop';

//

interface Config {
	onUpdate: (payload: { analysisResult: AudioAnalyzer.Result; animation: JSAnimation }) => void;
	createAnimation: () => JSAnimation;
}

export class PosterManager {
	private analyzer = new AudioAnalyzer.Analyzer();
	private animation: JSAnimation | undefined;

	private config?: Config;

	public readonly loop = new Loop({
		onPlay: () => {
			if (!this.config) return;
			if (!this.animation) this.animation = this.config.createAnimation();
			this.analyzer.start();
			this.animation.play();
		},
		onPause: () => {
			this.analyzer.stop();
			this.animation?.pause();
		},
		onUpdate: () => {
			this.config?.onUpdate({
				analysisResult: this.analyzer.analyze(),
				animation: this.animation!
			});
		}
	});

	setup(config: AudioAnalyzer.Config & Config) {
		this.config = config;
		this.analyzer.setConfig(config);
	}
}

export const posterManager = new PosterManager();
