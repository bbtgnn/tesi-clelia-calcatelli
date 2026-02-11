import P5 from 'p5';

import type { Result } from './audio-analyzer';

//

export class BarVisualizer {
	constructor(private getAnalysisResult: () => Result) {}

	attach(container: HTMLDivElement) {
		new P5((_) => {
			const margin = 10;
			const gap = 2;

			_.setup = () => {
				const canvas = _.createCanvas(400, 200);
				canvas.parent(container);
			};

			_.draw = () => {
				_.background(220);
				const { bars, highestBar } = this.getAnalysisResult();
				const barWidth = (_.width - 2 * margin - (bars.length - 1) * gap) / bars.length;
				const maxBarHeight = _.height - 2 * margin;
				for (let barIndex = 0; barIndex < bars.length; barIndex++) {
					const bar = bars[barIndex];
					const x = margin + barIndex * (barWidth + gap);
					const y = _.height - margin - bar.value * maxBarHeight;
					_.fill(255);
					if (barIndex === highestBar) {
						_.fill(255, 0, 0);
					}
					_.rect(x, y, barWidth, bar.value * maxBarHeight);
				}
			};
		});
	}
}
