<script>
	import { page } from '$app/stores';
	import { derived } from 'svelte/store';
	import { onMount } from 'svelte';
	import { animate, stagger } from 'animejs';
	import { darkMode } from '$lib/stores/darkMode.js'; // Assuming you have a store for dark mode
	import { tick } from 'svelte';
	const path = derived(page, ($page) => $page.url.pathname);
	$: if ($path === '/chatbot') animateChatbotNav();

	async function animateChatbotNav() {
		await tick();

		animate('.navigation ul li', {
			translateX: ['-150px', '0px'],
			opacity: 1,
			delay: stagger(500, { start: 900 }),
			duration: 2000,
			ease: 'cubicBezier(0.06, 0.9, 0.42, 0.99)'
		});
	}

	function toggleDarkMode() {
		darkMode.update((value) => !value);
	}

	$: {
		// You can still animate your navigation elements here based on $darkMode
		const img = document.querySelector('.navigation img');
		if (img) {
			animate(img, {
				opacity: 0,
				duration: 800,
				ease: 'easeInOutQuad',
				complete: () => {
					img.src = $darkMode
						? 'src/lib/images/buoy_title_dark.png'
						: 'src/lib/images/buoy_title_light.png';
					animate(img, {
						opacity: 1,
						duration: 800,
						ease: 'easeInOutQuad'
					});
				}
			});
		}

		animate('.navigation', {
			backgroundColor: $darkMode ? '#333' : '#F8FBF8',
			color: $darkMode ? '#FFF' : '#000',
			duration: 1000,
			ease: 'cubicBezier(0.5, 0.46, 0.09, 0.95)'
		});

		animate('.navigation a', {
			color: $darkMode ? '#FFF' : '#000',
			duration: 1000,
			ease: 'cubicBezier(0.5, 0.46, 0.09, 0.95)'
		});

		animate('hr', {
			backgroundColor: $darkMode ? '#FFF' : '#000',
			duration: 1000,
			ease: 'cubicBezier(0.5, 0.46, 0.09, 0.95)'
		});
	}
</script>

{#if $path === '/chatbot'}
	<div class="navigation-div" class:appear={$path == '/chatbot'}>
		<nav class="navigation">
			<img src="src\lib\images\buoy_title_light.png" alt="" class:fade={$path == '/chatbot'} />
			<ul>
				<li><a href="/"><span class="fa-solid fa-comment-medical"></span> New Chat</a></li>
				<li style="margin-bottom: 0;">
					<a href="/chatbot"><span class="fa-regular fa-trash-can"></span> Clear Chat</a>
				</li>
				<hr />
				<li><a href="/about">About</a></li>
				<li on:click={toggleDarkMode}>
					<button class="modes">{$darkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}</button
					>
				</li>
			</ul>
		</nav>
	</div>
{/if}

<style>
	.navigation-div {
		width: 15vw;
		padding: 3% 0 3% 3%;
		height: 100%;
		display: flex;
		flex-direction: column;
		box-sizing: border-box !important;
		position: absolute;
		bottom: 0;
	}

	.appear {
		animation: expandIn 0.9s cubic-bezier(0.46, 0.23, 0, 0.99) forwards;
	}

	hr {
		background: black;
		height: 2px; /* Add height */
		border: none; /* Remove default border */
		width: 100%; /* Optional: full width */
		margin: 1rem 0; /* Optional: spacing */
	}

	.fade {
		animation: fadeIn 0.9s cubic-bezier(0.46, 0.23, 0, 0.99) forwards;
		animation-delay: 0.9s;
	}

	@keyframes fadeIn {
		from {
			opacity: 0;
		}
		to {
			opacity: 1;
		}
	}
	@keyframes expandIn {
		from {
			height: 0;
		}
		to {
			height: 100%;
		}
	}
	.navigation {
		display: flex;
		flex-direction: column;
		align-items: center;
		width: 15vw;
		background: #f8fbf8;
		border-radius: 30px;
		height: 100%;
		flex-grow: 1;
		padding: 20%;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
	}

	.navigation ul {
		height: 100% !important;
		display: flex;
		align-items: center;
		flex-direction: column;
		opacity: 1;
		width: 100%;
		margin-top: 20%;
		overflow: hidden;
	}

	img {
		width: 5vw;
		height: auto;
		opacity: 0;
	}

	.navigation ul li {
		width: 100%;
		display: flex;
		align-items: center;
		background-color: transparent;
		transition: background-color 0.9s cubic-bezier(0.46, 0.23, 0, 0.99);
		border-radius: 10px;
		margin-bottom: 4%;
		padding: 1rem;
		cursor: pointer;
		opacity: 1;
	}

	.navigation ul li:hover {
		background-color: #d8ecf8;
		color: #1e4f91 !important;
	}

	.navigation ul li:hover a {
		color: #1e4f91 !important;
	}
	.navigation a {
		text-decoration: none;
		color: black;
		transition: color 0.3s ease;
	}
</style>
