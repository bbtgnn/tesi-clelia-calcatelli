<script lang="ts">
	import Poster1 from '$lib/posters/poster-1.svelte';
	import FftDemo from '$lib/fft/fft-demo.svelte';
	import { JSAnimation } from 'animejs';

	const BAR_COUNT = 20;

	let maxProgress = $state(1);
	let animation = $state<JSAnimation>();
	let duration = $state(1000);

	function handlePeakBinChange(
		barIndex: number,
		_binIndex: number,
		previousBarIndex: number,
		previousBinIndex: number,
		_totalBins: number
	) {
		// New maxProgress from bar index (0..1)
		maxProgress = BAR_COUNT > 1 ? barIndex / (BAR_COUNT - 1) : 1;

		const anim = animation;
		if (!anim) return;

		// old bin < new bin → reverse; otherwise normal
		anim.reversed = previousBinIndex >= 0 && previousBinIndex < _binIndex;
		anim.play();
	}
</script>

<Poster1 bind:animation {duration} {maxProgress} />

<main class="mx-auto max-w-2xl p-6">
	<FftDemo onPeakBinChange={handlePeakBinChange} />
</main>
