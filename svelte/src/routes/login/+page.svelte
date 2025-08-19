<script>
	import { onMount } from 'svelte';
	import { tick } from 'svelte';
	import { animate, stagger } from 'animejs';
	import { page } from '$app/state';
	import logo from '$lib/images/buoy_title_light.png';
	import soloLogo from '$lib/images/buoy_icon.png';
	import waves from '$lib/images/waves.png';
	import { derived } from 'svelte/store';
	const path = derived(page, ($page) => page.url.pathname);
	let isPassword = true;
	function changeInputType() {
		isPassword = !isPassword;
	}

	onMount(() => {
		const email = document.querySelector('.email-container');
		const password = document.querySelector('.password-container');
		const text = document.querySelector('.continue-text');
		const line1 = document.querySelector('.line1');
		const line2 = document.querySelector('.line2');
		// wait a tick to ensure DOM rendered
		if (email) {
			animate(email, {
				translateY: [-20, 0],
				opacity: [0, 1],
				duration: 1000,
				delay: 1000,
				ease: 'outQuad'
			});
		}

		if (password) {
			animate(password, {
				translateY: [-20, 0],
				opacity: [0, 1],
				duration: 1000,
				delay: 2000,
				ease: 'outQuad'
			});
		}

		if (line1) {
			animate(line1, {
				duration: 2000,
				translateY: [20, 0],
				opacity: [0, 1],
				delay: 1000,
				ease: 'outCubic'
			});
		}

		if (line2) {
			animate(line2, {
				duration: 2000,
				translateY: [20, 0],
				opacity: [0, 1],
				delay: 1000,
				ease: 'outQuad'
			});
		}
		if (text) {
			animate(text, {
				duration: 1000,
				translateY: [20, 0],
				opacity: [0, 1],
				ease: 'outQuad'
			});
		}
	});
</script>

<section class="login">
	<div class="login-container">
		<div class="inputs">
			<img src={logo} alt="Buoy Long Logo" />

			<h3>Welcome Back!</h3>
			<h1>Login</h1>

			<div class="forms">
				<div class="email-container">
					<input type="email" name="email-input" placeholder="hehe" />
					<label for="email-input">Email</label>
				</div>

				<div class="password-container">
					<input type={isPassword ? 'password' : 'text'} name="password-input" placeholder="hey" />
					<label for="password-input">Password</label>
					<button class="fa fa-eye" on:click={changeInputType}></button>
				</div>
			</div>

			<hr />

			<div class="bottom-forms">
				<button class="login-button" on:click={() => alert('hey')}>Login</button>

				<div class="continue-dialog">
					<div class="line1 line"></div>
					<div class="continue-text">Or continue with</div>
					<div class="line2 line"></div>
				</div>

				<ul class="social-media">
					<li><button class="fa-brands fa-github"></button></li>
					<li><button class="fa-brands fa-facebook"></button></li>
					<li><button class="fa-brands fa-google"></button></li>
				</ul>
			</div>
		</div>

		<div class="logo-container">
			<img src={soloLogo} alt="Buoy Main Logo" />
		</div>
	</div>
</section>

<style>
	hr {
		width: 50%;
		margin: 20px 0;
	}

	.fa.fa-eye {
		position: absolute;
		right: 10px;
		top: 50%;
		transform: translateY(-50%);
		pointer-events: auto;
		cursor: pointer;
	}

	.login {
		height: 100vh;
		width: 100vw;
		display: flex;
		justify-content: center;
		align-items: center;
		padding: 30px;
	}

	.login-container {
		display: flex;
		height: 100%;
		width: 100%;
		justify-content: center;
		align-items: center;
	}

	.inputs {
		background-color: #fffff0;
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: flex-start;
		padding: 80px;
		flex: 0 0 75%;
		height: 100%;
		border-radius: 20px 0 0 20px;
		line-height: 50px;
	}

	.inputs h3 {
		font-family: 'League Spartan', sans-serif;
		font-weight: bold;
		font-size: 20px;
		margin-bottom: 0px;
	}

	.inputs h1 {
		font-family: 'League Spartan', sans-serif;
		font-weight: bold;
		font-size: 50px;
		margin-bottom: 20px;
	}
	.inputs img {
		width: 10%;
		height: auto;
	}

	.forms {
		display: flex;
		flex-direction: column;
		width: 50%;
		position: relative;
		gap: 20px;
	}

	.email-container,
	.password-container {
		position: relative;
	}

	.email-container input::placeholder,
	.password-container input::placeholder {
		color: transparent;
	}

	.email-container label,
	.password-container label {
		display: inline-block;
		line-height: 1;
		position: absolute;
		left: 20px;
		top: 50%;
		transform: translateY(-50%);
		pointer-events: none;
		transition:
			top 0.5s ease,
			background-color 0.5s ease,
			color 1s ease;
		padding: 5px;
		border-radius: 5px;
		font-family: 'Outfit', sans-serif;
		font-weight: 500;
	}

	.email-container label > * {
		height: fit-content;
	}
	.email-container input:focus ~ label,
	.password-container input:not(:placeholder-shown) ~ label,
	.email-container input:not(:placeholder-shown) ~ label,
	.password-container input:focus ~ label {
		top: 0;
		background-color: #bd0000;
		color: white;
		height: fit-content;
	}

	input {
		width: 100%;
		background: skyblue;
		border-radius: 20px;
		padding: 10px;
		color: #fffff0;
		border: none;
		font-family: 'Outfit', sans-serif;
		transition: box-shadow 0.5s ease;
	}

	input:active,
	input:focus {
		border-color: transparent !important;
		outline: none !important;
		box-shadow: inset 0 0 3px 2px rgba(0, 0, 0, 0.5) !important;
	}

	.login-button {
		background: linear-gradient(to bottom right, crimson, #151515);
		font-family: 'Outfit', sans-serif;
		font-weight: bold;
		color: white;
		line-height: 1;
		padding: 20px;
		border-radius: 20px 0 20px 0;
		box-shadow: 0 0 4px 2px rgba(0, 0, 0, 0.5);
		transition: transform 0.5s ease;
	}

	.login-button:hover {
		transform: scale(1.05);
	}

	.bottom-forms {
		width: 50%;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
	}

	.continue-dialog {
		width: 100%;
		display: flex;
		gap: 20px;
		align-items: center;
	}

	.continue-text {
		text-wrap: nowrap;
	}
	.line {
		height: 1px;
		width: 100%;
		background: black;
	}

	.logo-container {
		background: url('/img/background-login.jpg') no-repeat center center;
		background-size: 100% 100%;
		height: 100%;
		flex: 0 0 25%;
		display: flex;
		align-items: center;
	}

	.logo-container img:first-child {
		width: 100%;
		height: auto;
		transform: translate(-50%, -25%) scale(1.2);
	}

	.social-media {
		display: flex;
		gap: 20px;
	}

	.social-media li {
		display: flex;
		justify-content: center;
		align-items: center;
		padding: 10px;
		background: #fffff0;
		border-radius: 50px;
		width: 100%;
		height: 100%;
		aspect-ratio: 1/1;
		box-shadow: 0 0 4px 2px rgba(0, 0, 0, 0.5);
		transition: transform 0.5s ease;
	}

	.social-media li:hover {
		transform: scale(1.1);
	}

	.social-media li button {
		width: 100%;
		height: auto;
		font-size: 30px;
	}
</style>
