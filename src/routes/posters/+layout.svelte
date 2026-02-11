<script lang="ts">
	import { ArrowLeft, ChartBar, Pause, Play } from '@lucide/svelte';
	import { posterManager } from '$lib/poster-manager';
	import { Button } from '$lib/shadcn/ui/button';

	//

	let { children } = $props();

	let showBarVisualizer = $state(false);
</script>

<div class="relative flex h-screen w-screen items-center justify-center overflow-hidden p-2 md:p-4">
	<div class="absolute top-0 left-0 p-2 md:p-4">
		<Button href="/" size="icon"><ArrowLeft /></Button>
	</div>

	<div class="absolute top-0 right-0 p-2 md:p-4">
		<div
			class={[
				'rounded-md bg-primary p-2',
				showBarVisualizer ? 'block' : 'hidden',
				'[&>canvas]:w-full [&>canvas]:rounded-xs'
			]}
			{@attach (c) => posterManager.barVisualizer.attach(c)}
		></div>
	</div>

	{@render children()}

	<div class="absolute right-0 bottom-0 p-2 md:p-4">
		<Button size="icon" onclick={() => (showBarVisualizer = !showBarVisualizer)}>
			<ChartBar />
		</Button>
		<Button size="icon" onclick={() => posterManager.loop.play()}><Play /></Button>
		<Button size="icon" onclick={() => posterManager.loop.pause()}><Pause /></Button>
	</div>
</div>
