import P5 from 'p5';

//

interface Config {
	onInit?: (sketch: P5) => void;
	onPause?: (sketch: P5) => void;
	onPlay?: (sketch: P5) => void;
	onUpdate: (sketch: P5) => void;
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
				config.onInit?.(_);
			};

			_.draw = () => {
				config.onUpdate(_);
			};
		});
	}

	play() {
		this.config.onPlay?.(this.sketch);
		this.sketch.loop();
	}

	pause() {
		this.config.onPause?.(this.sketch);
		this.sketch.noLoop();
	}
}
