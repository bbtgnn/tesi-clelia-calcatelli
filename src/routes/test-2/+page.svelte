<script lang="ts">
	import * as AudioAnalyzer from '$lib/audio-analyzer';
	import testSoundUrl from '$lib/fft/sounds/meccanismo-industriale-in-funzione.mp3?url';

	const analyzer = new AudioAnalyzer.Analyzer({
		audioUrl: testSoundUrl,
		barCount: 20,
		loop: true
	});

	const barVisualizer = new AudioAnalyzer.BarVisualizer(analyzer);
</script>

<div>
	<canvas width="400" height="400" {@attach (c) => barVisualizer.attach(c)}></canvas>
</div>
<button on:click={() => analyzer.start()}>Start</button>
<button on:click={() => analyzer.stop()}>Stop</button>
