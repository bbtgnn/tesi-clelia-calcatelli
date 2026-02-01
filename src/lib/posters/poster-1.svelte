<script lang="ts">
	import posterSvg from './poster-1.svg?raw';
	import { animate, svg, stagger, utils, JSAnimation } from 'animejs';

	//

	let { animation = $bindable<JSAnimation>(), duration = 1000, maxProgress = 1 } = $props();

	function attach(container: HTMLElement) {
		container.innerHTML = posterSvg;

		const svgEl = container.querySelector('svg');
		const end = container.querySelector('#end');
		const start = container.querySelector('#start');
		if (!start || !end || !svgEl) return;
		if (!(start instanceof SVGPathElement)) return;
		if (!(end instanceof SVGPathElement)) return;

		end.style.transformBox = 'fill-box';
		end.style.transformOrigin = '50% 50%';
		end.style.visibility = 'hidden';

		start.removeAttribute('id');
		start.classList.add('start');
		start.style.transformBox = 'fill-box';
		start.style.transformOrigin = '50% 50%';

		for (let i = 0; i < 40; i++) {
			const clone = start.cloneNode(true);
			start.parentNode?.appendChild(clone);
		}

		utils.set('.start', {
			rotate: -135
		});

		animation = animate('.start', {
			d: svg.morphTo(end),
			ease: 'linear',
			duration,
			loop: true,
			alternate: true,
			delay: stagger(50),
			rotate: 0,
			autoplay: false,
			onUpdate: (anim) => {
				if (anim.reversed) {
					if (anim.progress < maxProgress) {
						anim.pause();
					}
				} else {
					if (anim.progress > maxProgress) {
						anim.pause();
					}
				}
			}
		});
	}
</script>

<div class="h-[400px] w-[600px] [&>svg]:h-full [&>svg]:w-full" {@attach attach}></div>
