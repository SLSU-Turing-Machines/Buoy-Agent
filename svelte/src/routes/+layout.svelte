<script>
	import Header from './Header.svelte';
	import Login from './login/+page.svelte';
	import '../app.css';
	import Navigation from './Navigation.svelte';
	import { page } from '$app/stores';
	import { derived } from 'svelte/store';
	import bg from '$lib/images/background.webm';
	const path = derived(page, ($page) => $page.url.pathname);
	let videoEl;

	$effect(() => {
		setTimeout(() => {
			if (videoEl) {
				$path === '/chatbot' ? videoEl.pause() : videoEl.play();
			}
		}, 1000);
	});

	let { children } = $props();
</script>

<div class="app">
	<Header />
	<video
		bind:this={videoEl}
		autoplay
		loop
		muted
		playsinline
		class="background"
		class:blur={$path === '/chatbot'}
	>
		<source src={bg} type="video/webm" />
		Your browser does not support the video tag.
	</video>

	<div class="content">
		<Navigation />
		<main>
			{@render children()}
		</main>
	</div>
</div>

<style>
	.app {
		display: flex;
		flex-direction: column;
		height: 100vh;
		box-sizing: border-box;
		font-family: 'Inter', sans-serif;
	}
	.background {
		position: fixed;
		top: 0;
		left: 0;
		width: 100%;
		height: auto;
		display: block;
		z-index: -1;
		pointer-events: none;
		filter: blur(20px);
		transition: filter 2s ease;
	}

	.blur {
		filter: blur(5px);
	}
	.content {
		display: flex;
		flex: 1;
	}

	main {
		width: 100%;
		height: 100%;
	}
</style>
