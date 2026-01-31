<script lang="ts">
	import { onDestroy, tick } from 'svelte';
	import { loadPlayAndAnalyze } from '$lib/fft';
	import type { AudioAnalyzer } from '$lib/fft';
	// Default: use a local sound so the demo works without external URLs
	import defaultSoundUrl from '$lib/fft/sounds/meccanismo-industriale-in-funzione.mp3?url';

	interface Props {
		onPlay?: () => void;
		onStop?: () => void;
		/** Called when the peak (highest) bar changes (debounced). Receives: barIndex (0..BAR_COUNT-1), binIndex (0..totalBins-1), previousBarIndex/previousBinIndex (-1 if none), totalBins. */
		onPeakBinChange?: (
			barIndex: number,
			binIndex: number,
			previousBarIndex: number,
			previousBinIndex: number,
			totalBins: number
		) => void;
	}
	let { onPlay, onStop, onPeakBinChange }: Props = $props();

	const PEAK_BIN_DEBOUNCE_MS = 80;

	let url = $state(defaultSoundUrl as string);
	let analyzer = $state<AudioAnalyzer | null>(null);
	let loading = $state(false);
	let error = $state<string | null>(null);
	let canvasEl = $state<HTMLCanvasElement | null>(null);
	let rafId = $state<number | null>(null);

	// Refs for the rAF loop so the callback always has current analyzer/canvas (avoids stale $state in async)
	let analyzerRef: AudioAnalyzer | null = null;
	let canvasRef: HTMLCanvasElement | null = null;
	// Capture callback in ref so it's available inside rAF/setTimeout (props can be undefined there)
	let onPeakBinChangeRef: ((
		barIndex: number,
		binIndex: number,
		previousBarIndex: number,
		previousBinIndex: number,
		totalBins: number
	) => void) | null = null;
	// Peak debounce: emit bar + bin (current and previous) and totalBins; only when peak bar has been stable for PEAK_BIN_DEBOUNCE_MS
	let lastEmittedPeakBar: number | null = null;
	let lastEmittedPeakBin: number | null = null;
	let peakBinTimeoutId: ReturnType<typeof setTimeout> | null = null;
	let pendingPeakBar: number | null = null;
	let pendingPeakBin: number | null = null;
	let pendingTotalBins: number | null = null;

	const FFT_SIZE = 256;
	const BAR_COUNT = 20; // number of bars to draw (we'll average bins)

	function drawBars() {
		const a = analyzerRef;
		const c = canvasRef;
		if (!a || !c) return;

		const ctx = c.getContext('2d');
		if (!ctx) return;

		const data = a.getFFTData();
		const numBins = data.length;

		// Index of the highest bin this frame (raw FFT bins, 0..numBins-1)
		let peakBin = 0;
		for (let i = 1; i < numBins; i++) {
			if (data[i] > data[peakBin]) peakBin = i;
		}

		const binsPerBar = Math.max(1, Math.floor(numBins / BAR_COUNT));
		// Bar index (0..BAR_COUNT-1) that contains the peak bin — matches the drawn bars so no "overflow"
		const peakBarIndex = Math.min(BAR_COUNT - 1, Math.floor(peakBin / binsPerBar));

		// Emit peak bar change with debouncing: only reset the 80ms timer when the peak *bar* changes
		const cb = onPeakBinChangeRef;
		if (cb && peakBarIndex !== lastEmittedPeakBar) {
			const peakChanged = pendingPeakBar !== peakBarIndex;
			if (peakChanged) {
				pendingPeakBar = peakBarIndex;
				pendingPeakBin = peakBin;
				pendingTotalBins = numBins;
				if (peakBinTimeoutId != null) clearTimeout(peakBinTimeoutId);
				peakBinTimeoutId = setTimeout(() => {
					if (
						pendingPeakBar != null &&
						pendingPeakBin != null &&
						pendingTotalBins != null
					) {
						const prevBar = lastEmittedPeakBar ?? -1;
						const prevBin = lastEmittedPeakBin ?? -1;
						cb(
							pendingPeakBar,
							pendingPeakBin,
							prevBar,
							prevBin,
							pendingTotalBins
						);
						lastEmittedPeakBar = pendingPeakBar;
						lastEmittedPeakBin = pendingPeakBin;
						pendingPeakBar = null;
						pendingPeakBin = null;
						pendingTotalBins = null;
					}
					peakBinTimeoutId = null;
				}, PEAK_BIN_DEBOUNCE_MS);
			}
		}

		const w = c.width;
		const h = c.height;
		const barWidth = w / BAR_COUNT;
		const gap = 2;

		ctx.fillStyle = 'rgb(15 23 42)';
		ctx.fillRect(0, 0, w, h);
		const barValues: number[] = [];

		for (let i = 0; i < BAR_COUNT; i++) {
			let sum = 0;
			for (let j = 0; j < binsPerBar; j++) {
				sum += data[i * binsPerBar + j] ?? 0;
			}
			barValues.push(sum / binsPerBar);
		}

		// Data is 0–1 but often tiny (e.g. max ~0.01). Normalize to frame max so relative levels are visible.
		const frameMax = Math.max(...barValues, 1e-9);
		const minBarHeight = 2;

		for (let i = 0; i < BAR_COUNT; i++) {
			const value = barValues[i];
			const normalized = value / frameMax;
			const barHeight = Math.max(minBarHeight, normalized * h * 0.9);
			const x = i * barWidth + gap / 2;
			const y = h - barHeight;

			ctx.fillStyle = `hsl(${200 + normalized * 80} 70% 50%)`;
			ctx.fillRect(x, y, barWidth - gap, barHeight);
		}

		rafId = requestAnimationFrame(drawBars);
	}

	function stopVisualization() {
		if (rafId != null) {
			cancelAnimationFrame(rafId);
			rafId = null;
		}
		if (peakBinTimeoutId != null) {
			clearTimeout(peakBinTimeoutId);
			peakBinTimeoutId = null;
		}
		pendingPeakBar = null;
		pendingPeakBin = null;
		pendingTotalBins = null;
		lastEmittedPeakBar = null;
		lastEmittedPeakBin = null;
		onPeakBinChangeRef = null;
		analyzerRef = null;
		canvasRef = null;
	}

	async function handleLoadAndPlay() {
		error = null;
		loading = true;
		stopVisualization();
		if (analyzer) {
			analyzer.dispose();
			analyzer = null;
		}

		try {
			const result = await loadPlayAndAnalyze(url, {
				fftSize: FFT_SIZE,
				smoothing: 0.7,
				normalRange: true,
				loop: true
			});
			analyzer = result;
			result.play();
			onPlay?.();

			// Refs for the draw loop (rAF runs outside Svelte's reactive scope)
			analyzerRef = result;
			onPeakBinChangeRef = onPeakBinChange ?? null;
			await tick();
			canvasRef = canvasEl;

			if (canvasRef) {
				drawBars();
			}
		} catch (e) {
			error = e instanceof Error ? e.message : String(e);
		} finally {
			loading = false;
		}
	}

	function handleStop() {
		analyzer?.stop();
		onStop?.();
	}

	function handlePlay() {
		analyzer?.play();
		onPeakBinChangeRef = onPeakBinChange ?? null;
		onPlay?.();
	}

	onDestroy(() => {
		if (peakBinTimeoutId != null) clearTimeout(peakBinTimeoutId);
		stopVisualization();
		analyzerRef = null;
		canvasRef = null;
		analyzer?.dispose();
		analyzer = null;
	});
</script>

<div
	class="fft-demo rounded-xl border border-slate-200 bg-slate-50 p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900"
>
	<h2 class="mb-4 text-lg font-semibold text-slate-800 dark:text-slate-200">FFT demo</h2>

	<div class="mb-4 flex flex-wrap items-end gap-3">
		<label class="flex min-w-0 flex-1 flex-col gap-1">
			<span class="text-sm font-medium text-slate-600 dark:text-slate-400">Audio URL</span>
			<input
				type="text"
				bind:value={url}
				placeholder="https://… or path to audio file"
				class="rounded-md border border-slate-300 bg-white px-3 py-2 text-slate-900 shadow-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100"
			/>
		</label>
		<button
			type="button"
			onclick={handleLoadAndPlay}
			disabled={loading}
			class="rounded-md bg-indigo-600 px-4 py-2 font-medium text-white shadow-sm hover:bg-indigo-500 disabled:opacity-50"
		>
			{loading ? 'Loading…' : 'Load & play'}
		</button>
	</div>

	{#if error}
		<p class="mb-4 text-sm text-red-600 dark:text-red-400">{error}</p>
	{/if}

	{#if analyzer}
		<div class="mb-4 flex gap-2">
			<button
				type="button"
				onclick={handlePlay}
				class="rounded-md bg-emerald-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-emerald-500"
			>
				Play
			</button>
			<button
				type="button"
				onclick={handleStop}
				class="rounded-md bg-slate-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-slate-500"
			>
				Stop
			</button>
		</div>
	{/if}

	<div
		class="overflow-hidden rounded-lg border border-slate-200 bg-slate-900 dark:border-slate-700"
	>
		<canvas
			bind:this={canvasEl}
			width={640}
			height={200}
			class="block w-full max-w-full"
			aria-label="FFT frequency bars"
		></canvas>
	</div>

	<p class="mt-3 text-xs text-slate-500 dark:text-slate-400">
		Load an audio URL and click “Load & play” (user gesture required). The bars show real-time
		frequency analysis via Tone.js FFT.
	</p>
</div>
