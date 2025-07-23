<script>
	import { page } from '$app/stores';
	import { derived } from 'svelte/store';
	import buoyIcon from '$lib/images/buoy_icon.png';
	import { tick } from 'svelte';
	import { animate } from 'animejs';
	import { marked } from 'marked';
    import { darkMode } from '$lib/stores/darkMode.js';

	const path = derived(page, $page => $page.url.pathname);
 
    let stopper = true;
    let controller;
    let reader;

	$: if ($path === '/chatbot') animateChat();

	async function animateChat() {
		await tick();

		animate('.message', {
			opacity: [0, 1],
			translateY: ['-100px', '0px'],
			ease: 'cubicBezier(0.31, 0.52, 0.13, 0.84)',
			duration: 1000,
			delay: 2500
		});
	}

	let message = '';
	let messages = [];

	let aiStreamingIndex = -1;
	let buoyStreamingIndex = -1;
	let statusMessageIndex = -1; // NEW: for temporary status messages


    let scrollAnchor;

    $: messages, scrollToBottom();

    function scrollToBottom() {
        if (scrollAnchor) {
            scrollAnchor.scrollIntoView({ behavior: 'smooth' });
        }
    }

	function addMessage(from, text) {
		messages = [...messages, { from, text }];
	}

	function updateOrAddStreaming(type, text) {
		if (type === 'AI') {
			if (aiStreamingIndex === -1) {
				messages = [...messages, { from: 'Buoy Bot', text }];
				aiStreamingIndex = messages.length - 1;
			} else {
				messages[aiStreamingIndex].text = text;
			}
		} else if (type === 'Buoy') {
			if (buoyStreamingIndex === -1) {
				messages = [...messages, { from: 'Buoy Bot', text }];
				buoyStreamingIndex = messages.length - 1;
			} else {
				messages[buoyStreamingIndex].text = text;
			}
		}
	}

	function updateStatusMessage(text) {
		if (statusMessageIndex === -1) {
			messages = [...messages, { from: 'Buoy Bot', text }];
			statusMessageIndex = messages.length - 1;
		} else {
			messages[statusMessageIndex].text = text;
		}
	}

	function removeStreaming() {
		aiStreamingIndex = -1;
		buoyStreamingIndex = -1;
	}

	async function enterMessage() {
		if (!message.trim()) return;

        stopper = true;
        const intro = document.querySelector('.intro');

            intro.style.display = 'none'; // Hide the intro message
            await tick(); // Wait for the class to be applied

		const userMessage = message;
		addMessage('You', userMessage);
		message = '';

		const API_KEY = 'yawa';
		const API_URL = 'http://localhost:8050/buoy';
		let accumulatedContent = '';
		let aiBuffer = '';
		let buoyBuffer = '';
		let currentAI = '';
		let currentBuoy = '';

		updateStatusMessage('_Analyzing your message..._'); // REPLACED addMessage

		try {
			const response = await fetch(API_URL, {
				method: 'POST',
                signal: controller?.signal,
				headers: {
					'Content-Type': 'application/json',
					'X-API-KEY': API_KEY
				},
				body: JSON.stringify({ message: userMessage })
			});

			reader = response.body.getReader();
			const decoder = new TextDecoder();
           

			while (stopper) {
				const { done, value } = await reader.read();
				if (done) break;

				const chunk = decoder.decode(value, { stream: true });
				accumulatedContent += chunk;
				const events = accumulatedContent.split('\n\n');
				accumulatedContent = events.pop() || '';

				for (const event of events) {
					if (!event.startsWith('data: ')) continue;

					const json = event.slice(6);
					let parsed;
					try {
						parsed = JSON.parse(json);
					} catch (e) {
						console.error('Failed to parse SSE event:', json);
						continue;
					}

					const { status, response } = parsed;

					if (status === 'AI Analysis') {
						aiBuffer += response || '';
						currentAI = `🧠 AI Analysis:\n${aiBuffer}`;
						updateOrAddStreaming('AI', currentAI);
						continue;
					}

					if (status === 'buoy_response') {
						buoyBuffer += response || '';
						currentBuoy = `📡 Buoy Response:\n${buoyBuffer}`;
						updateOrAddStreaming('Buoy', currentBuoy);
						continue;
					}

					if (status === 'Done') {
						removeStreaming();

						if (response?.predicted_class) {
							const verdict = response.predicted_class;
							const confidence = Math.round(response.confidence_phishing * 100);
							const url = response.url;
							const verdictIcon = verdict.toLowerCase().includes('phishing') ? '⚠️' : '✅';
							const verdictMsg = `${verdictIcon} Final Verdict: ${verdict}\nConfidence: ${confidence}% phishing\nURL: ${url}`;
							messages[statusMessageIndex] = { from: 'Buoy Bot', text: verdictMsg }; // REPLACE streaming message
							statusMessageIndex = -1;
						} else if (response?.message) {
							messages[statusMessageIndex] = { from: 'Buoy Bot', text: `💬 ${response.message}` };
							statusMessageIndex = -1;
						}
					} else if (status) {
						updateStatusMessage(`${status}...`);
					}
                    
				}
			}
		} catch (err) {
			updateStatusMessage('❌ Error connecting to Buoy API. Please check your connection.');
			statusMessageIndex = -1;
			console.error(err);
		}
	}

    function stopStream() {
        stopper = false;
        controller?.abort();     
        reader?.cancel();        
        removeStreaming();       
        updateStatusMessage('⏹️ Streaming stopped.');
        statusMessageIndex = -1;
    }

	let showPadding = false;
	$: if ($path === '/chatbot') {
		setTimeout(() => {
			showPadding = true;
		}, 1040);
	}

    $: {

    animate('.chat-interface', {
      backgroundColor: $darkMode ? '#333' : '#F8FBF8',
      color: $darkMode ? '#FFF' : '#000',
      duration: 1000,
      ease: 'cubicBezier(0.5, 0.46, 0.09, 0.95)'
    });

    animate('.intro', {
      color: $darkMode ? '#FFF' : '#000',
      duration: 1000,
      ease: 'cubicBezier(0.5, 0.46, 0.09, 0.95)'
    });

    animate('.input-container', {
      backgroundColor: $darkMode ? '#333' : '#F8FBF8',
      duration: 1000,
      ease: 'cubicBezier(0.5, 0.46, 0.09, 0.95)'
    });
  }
</script>


<div class="main-container" class:expand={$path == '/chatbot'}>
	<div class="chat-interface" class:padded={showPadding}>
		<div class="chat-window">
			<div class="message">
                <div class="intro">
                <img src={buoyIcon} alt="BuoyBot Icon" class="buoyBot" />
				<h1>Welcome to the Buoy Bot!</h1>
				<br />
				<p>How can I assist you today?</p>
                </div>
				

				{#each messages as msg, index (index)}
					<div class={msg.from === 'You' ? 'user-message' : 'bot-message'} class:latest={index === messages.length - 1}>
						<h5>{msg.from}</h5>
						<p>{@html marked.parse(msg.text)}</p>
					</div>
				{/each}
                <div bind:this={scrollAnchor}></div>
			</div>
		</div>

		<div class="input-container">
			<input
				type="text"
				bind:value={message}
				placeholder="Type your message here..."
				on:keydown={(e) => {
					if (e.key === 'Enter') enterMessage();
				}} />
			<button on:click={enterMessage}>Send</button>
            <button on:click={stopStream}>Stop</button>
		</div>
	</div>
</div>


<style>
    .main-container{
        display: flex;
        justify-content: center;
        position: absolute;
        right: 0;
        height: 100%;
        width: 0vw;
        overflow: hidden;
        padding: 3%;
        box-sizing: border-box;
        color: white;
    }

    .expand{
        animation: expandMain 1s cubic-bezier(0.31, 0.52, 0.13, 0.84) forwards;
        animation-delay: 0.9s;
    }

    @keyframes expandMain{
        from{
            width: 0vw;
        }
        to{
            width: 83vw;
        }
    }

    .chat-interface {
        display: flex;
        flex-direction: column;
        height: 100%;
        width: 100%;
        background-color: #F8FBF8;
       overflow: hidden;
       padding: 0px;
       border-radius: 30px;
       transition: padding 0.5s ease;
       transition-delay: 0.9s;
       box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
    }

    .chat-interface.padded {
    padding: 20px;  
    }

    .chat-window {
        flex: 1;
        overflow-y: auto;
        border-radius: 8px;
        height: 100%;
    }

    .chat-window::-webkit-scrollbar {
  width: 8px;
}

.chat-window::-webkit-scrollbar-track {
  background: #F8FBF8;
}

.chat-window::-webkit-scrollbar-thumb {
  background: #F8FBF8;
  border-radius: 10px;
}

    .intro{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        color: black;
    }

    .message {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        margin-bottom: 20px;
        padding: 20px;
        color: black;
    }

    .buoyBot {
        width: 150px;
        height: auto;
        border-radius: 50%;
        margin-right: 10px;
    }

    h1{
        font-weight: bold;
    }

    p {
        font-size: 1.3rem;
        margin-bottom: 3px;
    }

    .input-container {
        display: flex;
        flex-direction: row;
        margin: 0 auto;
        width: 70%;
        padding: 10px;
        background-color: #F8FBF8;
         box-shadow: 
        inset 4px 4px 10px rgba(0, 0, 0, 0.3),
        inset -4px -4px 10px rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        outline: none;
        border: none;
        color: black;
    }

    input[type="text"] {
        width:95%;
        padding: 10px;
        border-radius: 10px;
        font-size: 16px;
        background: transparent;
        border: none;
        outline: none !important;
        transition: box-shadow 0.5s cubic-bezier(0.31, 0.52, 0.13, 0.84);
    }

    input[type="text"]:focus{
        outline: none !important;
        background: transparent;
        box-shadow: 0 0 6px 2px #007bff;
    }

    input{
        outline: none !important;
    }
    button {
        padding: 10px 15px;
        margin-left: 10px;
        background-color: #007bff;
        color: white;
        border: none;
        border-radius: 10px;
        cursor: pointer;
        font-size: 16px;
    }
    
    button:hover {
        background-color: #0056b3;
    }

    .user-message{
        align-self: flex-end;
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        background: linear-gradient(135deg, #a78bfa, #f472b6);
        border-radius: 15px 0 15px 15px;
        max-width: 90%;
        width: fit-content;
        padding: 5px 20px;
        margin-bottom: 2%;
        box-shadow: 5px 5px 10px rgba(0, 0, 0, 0.2);
    }



    .bot-message{
        align-self: flex-start;
        background: linear-gradient(135deg, #e6f4ea, #c7f9cc);
        border-radius: 0 15px 15px 15px;
        max-width: 90%;
        width: fit-content;
        padding: 2px 20px;
        margin-bottom: 2%;
        box-shadow: -5px -5px 10px rgba(0, 0, 0, 0.2);
    }

    h5{
        font-size: 18px;
        font-weight: bold;
    }
    .user-message p, .bot-message p{
        font-size: 13px;
        color: black;
    }
</style>