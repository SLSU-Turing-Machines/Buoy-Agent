<script>
	import welcome from '$lib/images/svelte-welcome.webp';
	import welcomeFallback from '$lib/images/svelte-welcome.png';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import logo from '$lib/images/buoy_title_light.png';
	import { animateHeaderOut } from '$lib/stores/header';
	import { animate, stagger, svg } from 'animejs';

	function fadeIn(node, { duration = 400 } = {}) {
		return {
			duration,
			css: (t) => `opacity: ${t}`
		};
	}

	let show = false;
	let semiTagline;

	$: {
	}
	onMount((duration = 100) => {
		// delay by one frame to trigger the transition
		requestAnimationFrame(() => {
			show = true;
		});
	});

	function handleNav() {
		goto('/chatbot');
	}
</script>

<svelte:head>
	<title>Home</title>
	<meta name="description" content="Buoy" />
</svelte:head>

<section>
	<div class="welcome-container">
		<div class="taglines">
			<h4>Stay Afloat. Stay Safe</h4>
			<h2>Introducing</h2>
			<img src={logo} alt="Buoy Main Logo" />
			<p bind:this={semiTagline}>
				Your lifeline against phishing threats, guarding you from the bait that hides beneath the
				surface.
			</p>
		</div>

		<!-- <lottie-player src="<URL HERE>" background="transparent"  speed="1"  style="width: 300px; height: 300px;" loop controls autoplay></lottie-player> -->
		{#if show}
			<button class="btn" transition:fadeIn={{ duration: 1000 }} on:click={handleNav}>
				Start Chatting
				<svg
					width="11"
					style="transform:translate(1px, -1px)"
					viewBox="0 0 11 12"
					fill="none"
					xmlns="http://www.w3.org/2000/svg"
				>
					<path
						d="M1.70985 4.5H7.7804M7.7804 4.5V10.5705M7.7804 4.5L0.780396 11.5"
						stroke="currentColor"
						stroke-width="1.3"
						stroke-linecap="round"
						stroke-linejoin="round"
					>
					</path>
				</svg>
			</button>
		{/if}
	</div>
</section>

<style>
	section {
		display: flex;
		justify-content: center;
		align-items: center;
		width: 100%;
		height: 100%;
	}

	.btn,
	.btn:active,
	.btn:focus {
		outline: none;
		border: none;
		background: linear-gradient(to bottom right, #87ceeb, #ffffff, #fffff0);
		border: 1.5px solid #4682b4;
		cursor: pointer;
		border-radius: 20px 0 20px 0;
		transition: transform 0.5s ease;
		display: flex;
		justify-content: center;
		align-items: center;
		gap: 20px;
		width: fit-content;
		height: auto;
		padding: 14px;
		box-shadow: 0 0 4px 2px rgba(0, 0, 0, 0.5);
	}

	button:hover {
		transform: translateY(-3px);
	}

	h4 {
		font-weight: bold;
		font-family: 'Outfit', sans-serif;
		font-size: clamp(0.8rem, 1.3vw, 1.4rem);
	}

	h2 {
		font-weight: bold;
		font-family: 'Outfit', sans-serif;
		font-size: clamp(1.5rem, 2.5vw, 2.8rem);
	}

	p {
		font-style: italic;
	}

	.welcome-container {
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;
	}

	.welcome-container img {
		width: 30%;
		height: auto;
	}

	.taglines {
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;
		margin-bottom: 20px;
	}
</style>
