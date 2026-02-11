<script lang="ts">
	import SvgRenderer from '$lib/components/svg-renderer.svelte';
	import { posterManager } from '$lib/poster-manager';
	import { createThrottled } from '$lib/utils/throttle';
	import { animate, stagger, svg, utils } from 'animejs';

	import audioUrl from './audio.mp3?url';
	import svgCode from './poster.svg?raw';

	//

	let previousHighestBar: number | undefined;

	const updatePreviousHighestBar = createThrottled((highestBar: number) => {
		previousHighestBar = highestBar;
	}, 40);

	posterManager.setup({
		audioUrl,
		barCount: 60,
		loop: true,

		onUpdate: ({ analysisResult: { highestBar }, animation }) => {
			updatePreviousHighestBar(highestBar);
			if (previousHighestBar === undefined || previousHighestBar === highestBar) return;

			if (highestBar === 0) {
				animation.pause();
			} else {
				animation.play();
			}

			// if (highestBar < previousHighestBar && !done) {
			// 	animation?.pause();
			// 	done = true;
			// }
			// if (highestBar > previousHighestBar && done) {
			// 	done = false;
			// 	animation?.play();
			// }
		},

		createAnimation: () => {
			utils.set('.start', {
				rotate: -45
			});
			// return animate('#end', {
			// 	rotate: 0
			// });
			return animate('.start', {
				d: svg.morphTo('#end'),
				ease: 'linear',
				duration: 500,
				loop: true,
				alternate: true,
				delay: stagger(20),
				rotate: 0,
				autoplay: false
			});
		}
	});
</script>

<SvgRenderer svg={svgCode} />
