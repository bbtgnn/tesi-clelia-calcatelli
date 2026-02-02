<script lang="ts">
	import type { ClassValue } from 'svelte/elements';

	type Props = {
		svg: string;
		class?: string;
		containerClass?: ClassValue;
		onMount?: (svgElement: SVGElement) => void;
	};

	let { svg, class: className, containerClass, onMount }: Props = $props();

	function renderSvg(container: HTMLElement) {
		container.innerHTML = svg;
		const svgElement = container.querySelector('svg');
		if (!svgElement) return;
		if (className) svgElement.classList.add(className);
		onMount?.(svgElement);
	}
</script>

<div
	class={['h-full w-full', '[&>svg]:h-full [&>svg]:w-full', containerClass]}
	{@attach renderSvg}
></div>
