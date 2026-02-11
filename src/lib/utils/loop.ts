import P5 from 'p5';

//

interface Config {
	onInit?: () => void;
	onPause?: () => void;
	onPlay?: () => void;
	onUpdate: () => void;
	frameRate?: number;
}

export class Loop {
	private sketch: P5;

	constructor(private config: Config) {
		this.sketch = new P5((_) => {
			_.setup = () => {
				_.noCanvas();
				_.frameRate(config.frameRate ?? 30);
				_.noLoop();
				config.onInit?.();
			};

			_.draw = () => {
				config.onUpdate();
			};
		});
	}

	play() {
		this.config.onPlay?.();
		this.sketch.loop();
	}

	pause() {
		this.config.onPause?.();
		this.sketch.noLoop();
	}
}
