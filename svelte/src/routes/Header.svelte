<script>
	import { page } from '$app/stores';
	import logo from '$lib/images/svelte-logo.svg';
	import github from '$lib/images/github.svg';
	import { derived } from 'svelte/store';
	import buoyTitleDark from '$lib/images/buoy_title_dark.png';
	import light from '$lib/images/buoy_title_light.png';

  // Derive the current path to change layout styles
  const path = derived(page, $page => $page.url.pathname);

</script>

<header class:slide-bottom={$path === '/chatbot'}>
	<h1><img src={light} alt="Buoy Title"/></h1>
</header>

<style>
	header {
		width: 100vw;
		height: 10vh;
		background-color: transparent;
		padding: 10px;
		display: flex;
		position: fixed;
		top: 0;
		transition: transform 0.5s ease, opacity 0.5s ease;
		opacity: 1;
		transform: translateY(0);
	}

	img {
		height: 100%;
		width: auto;
		margin-left: 3%;
	}

	h1 {
		color: white;
		font-size: 2rem;
		margin: 0;
		
		transform: translateY(0);
	}

	.slide-bottom {
		transform: translateY(-10vw);
		opacity: 0;
	}

	.header-disappear {
		animation: fadeOut 1s forwards;
	}

	@keyframes fadeOut {
		0% {
			opacity: 1;
		}
		99% {
			opacity: 0;
		}
		100%{
			opacity: 0;
			display: none;
		}
	}
</style>
