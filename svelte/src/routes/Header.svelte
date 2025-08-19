<script>
	import { page } from '$app/stores';
	import logo from '$lib/images/svelte-logo.svg';
	import github from '$lib/images/github.svg';
	import { derived } from 'svelte/store';
	import buoyTitleDark from '$lib/images/buoy_title_dark.png';
	import light from '$lib/images/buoy_title_light.png';
	import { onMount, tick } from 'svelte';
	import { animate, stagger, onScroll } from 'animejs';
	import icon from '$lib/images/buoy_icon.png';
	import { animateHeaderOut } from '$lib/stores/header';
	import { goto } from '$app/navigation';
	// Derive the current path to change layout styles
	const path = derived(page, ($page) => $page.url.pathname);
	let header = null;
	onMount(() => {
		header = document.querySelector('header');
	});

	$: {
		if ($path === '/chatbot' || $path === '/login') {
			animate(header, {
				translateY: [0, -200],
				opacity: [0, 1],
				duration: 1500,
				ease: 'outCubic'
			});
		} else {
			animate(header, {
				translateY: [-50, 0],
				opacity: [0, 1],
				duration: 1500,
				ease: 'outCubic'
			});
		}
	}

	function goToLogin() {
		goto('/login');
	}
</script>

<header class:slide-bottom={$path === '/chatbot'}>
	<ul class="header-list">
		<li>
			<img src={icon} alt="Buoy Main Icon" />
		</li>
		<li>
			<h1>Buoy</h1>
		</li>
		<li>
			<div>
				<ul class="forms">
					<li><button on:click={goToLogin}>Login</button></li>
					<li><button on:click={goToSignUp}>Sign Up</button></li>
				</ul>
			</div>
		</li>
	</ul>
</header>

<style>
	header {
		width: 100vw;
		height: 10vh;
		display: flex;
		position: fixed;
		opacity: 1;
		color: #fffff0;
		font-family: 'League Spartan', sans-serif;
		margin-top: 20px;
		justify-content: center;
	}

	.header-list {
		width: 50%;
		height: 100%;
		display: flex;
		justify-content: space-between;
		background: #28282b;
		border-radius: 20px;
		padding: 10px;
	}

	.header-list li {
		display: flex; /* so image can center */
		justify-content: center;
		align-items: center;
		overflow: hidden;
		pointer-events: auto;
	}

	.header-list li button {
		background-color: blue;
	}

	.header-list li button:hover {
		background-color: red;
	}

	.header-list li:nth-child(3) div .forms {
		display: flex;
		gap: 20px;
	}

	.header-list img {
		max-height: 100%; /* don’t exceed li height */
		max-width: 100%; /* don’t exceed li width */
		object-fit: contain;
	}
</style>
