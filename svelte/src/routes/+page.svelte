<script>
	import welcome from '$lib/images/svelte-welcome.webp';
	import welcomeFallback from '$lib/images/svelte-welcome.png';
</script>

<svelte:head>
	<title>Home</title>
	<meta name="description" content="Svelte demo app" />
</svelte:head>

<section>
	<div class="welcome-container">
		<h1>Welcome to Buoy!</h1>
		<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse et velit sed dui mattis pellentesque. Duis tempor mauris nec enim condimentum interdum.</p>
		<br>
		<a href="/about" class="btn">Start Chatting</a>
	</div>
</section>

<style>
	section {
		display: flex;
		justify-content: left;
		margin-top: 50px;
		width: 60%;
	}

	.btn,
	.btn:active,
	.btn:focus{
		outline: none;
		border: none;
		background-color: #87ceeb2f;
		border: 1.5px solid #4682B4;
		cursor: pointer;
		border-radius: 50px;
		text-align: left;
		padding: 10px;
		padding-left: 20px;
		padding-right: 250px;
	}

	.btn:hover {
		background-color: #87ceeb;
	}

	h1{
		font-weight: bold;
	}

</style>
