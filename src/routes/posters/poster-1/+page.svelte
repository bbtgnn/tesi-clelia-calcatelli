<script lang="ts">
	import * as AudioAnalyzer from '$lib/audio-analyzer';
	import SvgRenderer from '$lib/components/svg-renderer.svelte';
	import { Loop } from '$lib/utils/loop';
	import { createThrottled } from '$lib/utils/throttle';
	import { animate, stagger, svg, utils, type JSAnimation } from 'animejs';

	import { setControls } from '../+layout.svelte';
	import audioUrl from './audio.mp3?url';
	import svgCode from './poster.svg?raw';

	//

	const analyzer = new AudioAnalyzer.Analyzer({
		audioUrl: audioUrl,
		barCount: 20,
		loop: true
	});

	const duration = 1000;

	let previousHighestBar: number | undefined;
	let animation: JSAnimation | undefined;

	const updatePreviousHighestBar = createThrottled((highestBar: number) => {
		previousHighestBar = highestBar;
	}, 40);

	let done = false;

	const loop = new Loop({
		onPlay: () => {
			if (!animation) {
				createAnimation();
			}
			analyzer.start();
			animation?.play();
		},
		onPause: () => {
			analyzer.stop();
			animation?.pause();
		},
		onUpdate: () => {
			const { highestBar } = analyzer.analyze();
			updatePreviousHighestBar(highestBar);
			if (previousHighestBar === undefined || previousHighestBar === highestBar) return;

			if (highestBar < previousHighestBar && !done) {
				animation?.pause();
				done = true;
			}
			if (highestBar > previousHighestBar && done) {
				done = false;
				animation?.play();
			}

			// console.log(highestBar, previousHighestBar);
			// if

			// animation?.pause();
			// animation?.reverse();
			// animation?.play();

			// if (previousHighestBar > highestBar) {
			// 	animation?.reverse();
			// 	animation?.play();
			// }
			// else {

			// }

			// maxProgress = highestBar / (bars.length - 1) + 0.2;
			// console.log(maxProgress);

			// if (!animation) return;
			// animation.reversed = highestBar < previousHighestBar;
			// animation.play();
		}
	});

	setControls({
		onStart: () => loop.play(),
		onStop: () => loop.pause()
	});

	function createAnimation() {
		utils.set('.start', {
			rotate: -45
		});

		animation = animate('.start', {
			d: svg.morphTo('#end'),
			ease: 'linear',
			duration,
			loop: true,
			alternate: true,
			delay: stagger(100),
			rotate: 0,
			autoplay: false
		});
	}
</script>

<SvgRenderer svg={svgCode} />
