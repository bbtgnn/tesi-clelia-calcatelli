<script lang="ts">
	import SvgRenderer from '$lib/components/svg-renderer.svelte';
	import svgCode from './poster-1.svg?raw';
	import { animate, svg, stagger, utils, type JSAnimation } from 'animejs';
	import * as AudioAnalyzer from '$lib/audio-analyzer';
	import audioUrl from '$lib/fft/sounds/meccanismo-industriale-in-funzione.mp3?url';
	import { setControls } from '../+layout.svelte';
	import { Loop } from '$lib/utils/loop';
	import { createThrottled } from '$lib/utils/throttle';

	//

	const analyzer = new AudioAnalyzer.Analyzer({
		audioUrl: audioUrl,
		barCount: 20,
		loop: true
	});

	const duration = 1000;
	let maxProgress = 1;
	let previousHighestBar: number | undefined;
	let animation: JSAnimation | undefined;

	const updatePreviousHighestBar = createThrottled((highestBar: number) => {
		previousHighestBar = highestBar;
	}, 40);

	let done = false;

	const loop = new Loop({
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
		onStart: () => {
			analyzer.start();
			loop.play();
			animation?.play();
		},
		onStop: () => {
			analyzer.stop();
			loop.pause();
			animation?.pause();
		}
	});

	function setupSvg(el: SVGElement) {
		const end = el.querySelector('#end');
		const start = el.querySelector('#start');
		if (!start || !end) return;
		if (!(start instanceof SVGPathElement)) return;
		if (!(end instanceof SVGPathElement)) return;

		end.style.transformBox = 'fill-box';
		end.style.transformOrigin = '50% 50%';
		end.style.visibility = 'hidden';

		start.removeAttribute('id');
		start.classList.add('start');
		start.style.transformBox = 'fill-box';
		start.style.transformOrigin = '50% 50%';

		const frag = document.createDocumentFragment();
		for (let i = 0; i < 20; i++) {
			const clone = start.cloneNode();
			frag.appendChild(clone);
		}
		start.parentElement?.appendChild(frag);
	}

	function createAnimation() {
		utils.set('.start', {
			rotate: -90
		});

		animation = animate('.start', {
			d: svg.morphTo('#end'),
			ease: 'linear',
			duration,
			loop: true,
			alternate: true,
			delay: stagger(100),
			rotate: 0,
			autoplay: false,
			onUpdate: (anim) => {
				// if (anim.reversed) {
				// 	if (anim.progress < maxProgress) {
				// 		anim.pause();
				// 	}
				// } else {
				// 	if (anim.progress > maxProgress) {
				// 		anim.pause();
				// 	}
				// }
			}
		});
	}
</script>

<SvgRenderer
	svg={svgCode}
	onMount={(e) => {
		setupSvg(e);
		createAnimation();
	}}
/>
