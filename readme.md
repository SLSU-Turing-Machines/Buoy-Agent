# Buoy AI Agent

An extension of **TheTuringMachine's AI Pipeline**, enhanced with an intelligent Ollama LLM agent for phishing detection and decentralized cybersecurity automation.

## Installation

1. Ensure you are using **Python 3.10.11**, then install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

2. Install **Ollama** (required for LLM-based analysis):

   * Follow installation instructions from: [https://ollama.com/download](https://ollama.com/download)

3. Pull the **Gemma 2B** model:

   ```bash
   ollama pull gemma:2b
   ```

   > ⚠️ Ollama must be running for the backend to communicate with the LLM.

## Running the Server

Use the provided deployment script:

### On Linux/macOS:

```bash
./build_and_deploy.sh
```

### On Windows:

```bat
build_and_deploy.bat
```

This will:

* Build the Svelte frontend
* Deploy to the Internet Computer via DFX
* Launch the Flask backend server

## Environment Configuration

Create a `.env` file in the project root directory with the following content:

```env
buoy=your_server_key_here
```

Replace `your_server_key_here` with your actual API key or secret token.


