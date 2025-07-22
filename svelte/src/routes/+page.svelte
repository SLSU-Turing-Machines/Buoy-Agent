<script>
	import welcome from '$lib/images/svelte-welcome.webp';
	import welcomeFallback from '$lib/images/svelte-welcome.png';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	 function fadeIn(node, { duration = 400 } = {}) {
		return {
		duration,
		css: t => `opacity: ${t}`
		};
  	}

  let show = false;

    onMount((duration = 100) => {
    // delay by one frame to trigger the transition
    requestAnimationFrame(() => {
      show = true;
    });
  });

  function handleNav(){
	goto('/chatbot');
  }
</script>

<svelte:head>
	<title>Home</title>
	<meta name="description" content="Buoy" />
</svelte:head>

<section>
	<div class="welcome-container">
		<h1>Welcome to Buoy!</h1>
		<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec augue nulla, consequat at tellus in, mattis eleifend lacus. Duis luctus commodo ornare. </p>
		<!-- <lottie-player src="<URL HERE>" background="transparent"  speed="1"  style="width: 300px; height: 300px;" loop controls autoplay></lottie-player> -->
		{#if show}
		<button class="btn" transition:fadeIn={{ duration: 1000 }} on:click={handleNav}>
			Start Chatting
		</button>
		{/if}
		
	</div>
</section>

<style>
	section {
		display: flex;
		justify-content: flex-start;
		align-items: center;
		width: 50%;
		margin-top: 15vh;
		margin-left: 100px;
	}

	.btn,
	.btn:active,
	.btn:focus{
		outline: none;
		border: none;
		background-color: #87ceeb2f;
		border: 1.5px solid #4682B4;
		cursor: pointer;
		width: 500px;
		height: 40px;
		border-radius: 50px;
		transition: background-color 0.3s ease, color 0.3s ease;
	}

	button:hover {
		background-color: #4682B4;
		color: white;
	}

	h1 {
		font-weight: bold;
	}

</style>
