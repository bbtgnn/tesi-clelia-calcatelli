<script lang="ts">
	import { ArrowLeft, ChartBar, Pause, Play } from '@lucide/svelte';
	import Popover from '$lib/components/popover.svelte';
	import { posterManager } from '$lib/poster-manager';
	import { Button } from '$lib/shadcn/ui/button';

	let { children } = $props();
</script>

<div class="relative flex h-screen w-screen items-center justify-center overflow-hidden p-2 md:p-4">
	<div class="absolute top-0 left-0 p-2 md:p-4">
		<Button href="/" size="icon"><ArrowLeft /></Button>
	</div>
	{@render children()}
	<div class="absolute right-0 bottom-0 p-2 md:p-4">
		<Popover>
			{#snippet trigger({ props })}
				<Button size="icon" {...props}><ChartBar /></Button>
			{/snippet}
			{#snippet content()}
				<div>
					<h1>Controls</h1>
				</div>
			{/snippet}
		</Popover>
		<Button size="icon" onclick={() => posterManager.loop.play()}><Play /></Button>
		<Button size="icon" onclick={() => posterManager.loop.pause()}><Pause /></Button>
	</div>
</div>
