import P5 from 'p5';

//

interface Config {
	onStart?: () => void;
	onUpdate: () => void;
	frameRate?: number;
}

export class Loop {
	private sketch: P5;

	constructor(config: Config) {
		this.sketch = new P5((_) => {
			_.setup = () => {
				_.noCanvas();
				_.frameRate(config.frameRate ?? 30);
				_.noLoop();
				config.onStart?.();
			};

			_.draw = () => {
				config.onUpdate();
			};
		});
	}

	play() {
		this.sketch.loop();
	}

	pause() {
		this.sketch.noLoop();
	}
}
