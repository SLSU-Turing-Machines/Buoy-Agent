<script>
    import { page } from '$app/stores';
    import { derived } from 'svelte/store';
    import buoyIcon from '$lib/images/buoy_icon.png';
	import { tick } from 'svelte';
	import { animate } from 'animejs';

    const path = derived(page, $page => $page.url.pathname);

    $: if ($path === '/chatbot') animateChat();

    async function animateChat(){
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
    let messages = [
    ];

    async function enterMessage() {
    if (message.trim()) {
        messages = [...messages, { from: 'You', text: message }];

        await tick();
        animate('.latest', {
            opacity: [0, 1],
            translateX: ['100px', '0px'],
            duration: 800,
            ease: 'cubicBezier(0.31, 0.52, 0.13, 0.84)'
        });

        setTimeout(() => {
        messages = [...messages, { from: 'Buoy Bot', text: 'I heard you!' }];
        }, 1000);
        message = '';
    }
    }

    let showPadding = false;
        $: if ($path === '/chatbot') {
        setTimeout(() => {
            showPadding = true;
        }, 1040);
    }

</script>

<div class = "main-container" class:expand={$path == '/chatbot'}>
    <div class="chat-interface" class:padded={showPadding}>
        <div class="chat-window">
            <div class="message">
                <img src={buoyIcon} alt="BuoyBot Icon" class="buoyBot"/>
                <h1>Welcome to the Buoy Bot!</h1>
                <br> 
                <p>How can I assist you today?</p>
               {#each messages as msg, index (index)}
                    <div class={msg.from === 'You' ? 'user-message' : 'bot-message'} class:latest={index === messages.length - 1}>
                    <h5>{msg.from}</h5>
                    <p>{msg.text}</p>
                    </div>
                {/each}
            </div>
             
        </div>
        <div class="input-container">
                    <input type="text" bind:value={message} placeholder="Type your message here..." on:keydown={(e) => {
                    if (e.key === 'Enter'){
                        enterMessage();
                    }
                    }}/>
                    <button>Send</button>
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
        background: #205930aa;
        border: 2px solid #00ff04;
        border-radius: 15px 0 15px 15px;
        max-width: 90%;
        width: fit-content;
        padding: 5px 20px;
        margin-bottom: 2%;
    }



    .bot-message{
        align-self: flex-start;
        background: #ff008cd1;
        border: 2px solid #ff0062;
        border-radius: 0 15px 15px 15px;
        max-width: 90%;
        width: fit-content;
        padding: 2px 20px;
        margin-bottom: 2%;
    }

    h5{
        font-size: 18px;
        font-weight: bold;
    }
    .user-message p, .bot-message p{
        font-size: 13px;
        color: white;
    }
</style>