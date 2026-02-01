import P5 from 'p5';
import type { Analyzer } from './audio-analyzer';

//

export class BarVisualizer {
	private sketch: P5 | null = null;

	constructor(private analyzer: Analyzer) {}

	attach(canvas: HTMLCanvasElement) {
		this.sketch = new P5((_) => {
			const margin = 10;
			const gap = 2;

			_.setup = () => {
				_.createCanvas(400, 200, 'p2d', canvas);
			};

			_.draw = () => {
				_.background(220);
				const { bars } = this.analyzer.analyze();
				const barWidth = (_.width - 2 * margin - (bars.length - 1) * gap) / bars.length;
				const maxBarHeight = _.height - 2 * margin;
				for (let barIndex = 0; barIndex < bars.length; barIndex++) {
					const bar = bars[barIndex];
					const x = margin + barIndex * (barWidth + gap);
					const y = _.height - margin - bar.value * maxBarHeight;
					_.fill(255);
					_.rect(x, y, barWidth, bar.value * maxBarHeight);
				}
			};
		});
	}
}
