'''
BUOY AI Phishing Detection Agent
This module uses an LLM (Ollama) to decide which tools to run for phishing detection
and to explain the final verdict based on tool results.

It provides a simple interface to interact with the LLM and handle tool selection
and explanation generation.

This code is part of the BUOY AI project, which aims to provide an AI-driven phishing detection solution.
Copyright (c) 2025 TheTuringMachines. All rights reserved.
'''

# agent/llm_agent.py
import re
import json
import shutil
import requests

DEFAULT_OLLAMA_MODEL = "gemma2:2b"  # fallback default model
OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_REGISTRY = "model/model_registry.json"

#read model registry to get options for tools
def read_model_registry(include_prompt_format=False):
    """
    Read the model registry JSON file to get available models.
    
    Args:
        include_prompt_format (bool): If True, returns a formatted string
                                      with model names, descriptions, and accuracy.

    Returns:
        dict | (dict, str): Just the model dictionary or (dict, formatted string)
    """
    try:
        with open(MODEL_REGISTRY, 'r', encoding='utf-8') as f:
            models = json.load(f)
    except FileNotFoundError:
        print(f"[Error] Model registry file not found: {MODEL_REGISTRY}")
        return {} if not include_prompt_format else ({}, "")
    except json.JSONDecodeError as e:
        print(f"[Error] Failed to parse model registry JSON: {str(e)}")
        return {} if not include_prompt_format else ({}, "")
    except Exception as e:
        print(f"[Error] Unexpected error reading model registry: {str(e)}")
        return {} if not include_prompt_format else ({}, "")

    if include_prompt_format:
        formatted = []
        for key, meta in models.items():
            desc = meta.get("description", "No description available")
            acc = meta.get("accuracy", "N/A")
            formatted.append(f"{key} - {desc} (training accuracy: {acc:.4f})")
        return models, "\n".join(formatted)

    return models

def is_ollama_installed():
    return shutil.which("ollama") is not None

def call_ollama(prompt, model=DEFAULT_OLLAMA_MODEL):
    """
    Call the Ollama REST API to get a response for the given prompt.
    Returns the full response as a string.
    """
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False  # We want the full response, not streaming
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=60)
        response.raise_for_status()
        
        # Ollama returns a JSON object with 'response' key
        json_data = response.json()
        return json_data.get("response", "")
        
    except requests.exceptions.Timeout:
        return "[Error] Request timed out. Please try again."
    except requests.exceptions.ConnectionError:
        return "[Error] Could not connect to Ollama. Please ensure Ollama is running."
    except requests.exceptions.RequestException as e:
        return f"[Error] Ollama request failed: {str(e)}"
    except json.JSONDecodeError as e:
        return f"[Error] Failed to parse JSON response: {str(e)}"
    except Exception as e:
        return f"[Error] Unexpected error in call_ollama: {str(e)}"

def call_ollama_stream(prompt, model="gemma2:2b"):
    """
    Stream response from Ollama REST API as a generator.
    Yields chunks of the response as they arrive.
    """
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": True
    }
    try:
        with requests.post(OLLAMA_API_URL, json=payload, stream=True) as response:
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode("utf-8"))
                        content = data.get("response")
                        if content:
                            print("[LLM stream] Output:", content)
                            yield content
                    except json.JSONDecodeError as e:
                        print("[LLM stream] JSON error:", e)
    except requests.exceptions.RequestException as e:
        yield f"[Error] Ollama request failed: {str(e)}"

def choose_tools(url, model=DEFAULT_OLLAMA_MODEL):
    '''
    Use the LLM to decide which tools to run based on the URL characteristics.
    Returns a list of tool names to run.
    '''
    _, formatted_registry = read_model_registry(include_prompt_format=True)
    prompt = f"""
You are Buoy, an AI phishing detection assistant.
A user submitted this URL: {url}

Available tools:
{formatted_registry}

Based on the URL characteristics, decide which tools should be run.
Note if you think the url isn't suspicious, default to running xgboost
Respond ONLY in JSON with a list of tool names to run. Example:

```json
{{ "tools_to_run": ["base_model"] }}
```
Do not include any other text or explanations.
"""
    raw_response = call_ollama(prompt, model=model)
    print("[LLM response] Tools to run:", raw_response)
    try:
        json_text = extract_json_block(raw_response)
        print("[LLM response] Parsed JSON:", json_text)
        parsed = json.loads(json_text)
        return parsed.get("tools_to_run", [])
    except Exception as e:
        print("[LLM fallback] Error parsing response:", e)
        print("Full response:", raw_response)
        return ["base_model"]

def extract_json_block(text):
    """
    Extract first valid JSON block from a markdown-like string.
    Example: from ```json ... ``` or a plain JSON object.
    """
    json_match = re.search(r"```json\s*({.*?})\s*```", text, re.DOTALL)
    if json_match:
        return json_match.group(1)

    fallback_match = re.search(r"{.*}", text, re.DOTALL)
    if fallback_match:
        return fallback_match.group(0)

    return None

def explain_verdict(results, context=None, model=DEFAULT_OLLAMA_MODEL):
    prompt = f"""
You are Buoy, a website phishing detection assistant. You are given the results from several tools, as well as contextual page features.

Tool results:
{json.dumps(results, indent=2)}

Context features (non-tool signals):
{json.dumps(context or {}, indent=2)}

Based on the above, explain the final verdict (phishing or legit).
Do not soley rely on the tool results, but also consider the context features.
Output just a short paragraph explanation. And tips for the user on how to stay safe online.
"""
    return call_ollama(prompt, model=model).strip()

def stream_explanation_verdict(results, context=None, model=DEFAULT_OLLAMA_MODEL):
    """
    Streams the explanation verdict using Ollama in real-time.
    Yields partial outputs line by line as they are generated.
    """
    prompt = f"""
You are Buoy, a phishing detection assistant. You are given the results from several tools, as well as contextual page features.

Tool results:
{json.dumps(results, indent=2)}

Context features (non-tool signals):
{json.dumps(context or {}, indent=2)}

Analyze the provided information to determine if the presented scenario is phishing or legitimate.

Do not solely rely on the tool results, but also consider the context features.
Consider their training accuracy as stated before.

Your output must begin with a JSON object containing only the verdict. The JSON format should be:

```json
  {{"verdict": "phishing"}}
```
Immediately following the JSON output, provide a concise paragraph (not in JSON) explaining why you reached that verdict. Detail the specific indicators or lack thereof that led to your conclusion (e.g., suspicious URLs, grammatical errors, generic greetings, secure connection).
After the explanation, offer general tips (not in JSON) for users to enhance their online safety.
If the verdict is "phishing," additionally provide the following information (not in JSON):
Hosting Provider: Identify the likely hosting provider of the malicious content. (if available)
Abuse Contact: Furnish the appropriate abuse contact information for the hosting provider (if readily available).
Reporting Guide: Offer clear, step-by-step guidance on how the user can report this phishing attempt to relevant authorities or organizations. (default to Google Safe Browsing, https://safebrowsing.google.com/safebrowsing/report_phish/)

"""
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": True
    }
    try:
        with requests.post(OLLAMA_API_URL, json=payload, stream=True) as response:
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode("utf-8"))
                        content = data.get("response")
                        if content:
                            print("[LLM stream] Output:", content)
                            yield content
                    except json.JSONDecodeError as e:
                        print("[LLM stream] JSON error:", e)
    except requests.exceptions.RequestException as e:
        yield f"[Error] Ollama request failed: {str(e)}"

def ask_llm(prompt, model="gemma2:2b"):  
    """
    Ask the LLM and return a streaming generator with a contextual system prompt.
    """
    full_prompt = f"""
You are Buoy, an autonomous AI phishing detection assistant and cybersecurity agent.

Buoy is a lightweight, real-time AI agent built to detect, investigate, and block phishing threats with zero user input. It combines a modular threat intelligence pipeline with secure decentralized infrastructure.

🔐 Your system architecture includes:
- A stacked machine learning ensemble using CNN-LSTM and XGBoost classifiers.
- A modular orchestrator that decides which tools to run (WHOIS, DNS, threat DBs, LLM reasoning).
- A secure scraping system built on **Internet Computer Protocol (ICP)** using **Wasm-based canisters**.

📦 **ICP Canister-Based Isolation Layer**:
Phishing websites are scraped through isolated WebAssembly containers deployed on ICP. These canisters safely fetch, sanitize, and analyze website content **without risk of JavaScript injection, malware, or system compromise**. This containerized architecture ensures that Buoy can analyze malicious content in a **trustless, tamper-proof**, and **fully decentralized** environment.

🧠 Your role as Buoy:
- Interpret partial and final results from detection tools
- Make decisions autonomously on what analysis step to run next
- Explain reasoning in clear language to end users
- Provide cybersecurity insights and educate users when needed

🧬 Mission:
Buoy was created by *TheTuringMachines*, a team of Bachelor of Computer Engineering students at **Southern Luzon State University**, Philippines. It was built for the **World Computer Hackers League (WCHL25)**, hosted by **DoraHacks**, and leverages **Internet Computer Protocol (ICP)** for decentralization and safety.

You are open source, decentralized, and free to use.


A user submitted this input for analysis:
{prompt}

Respond thoughtfully based on the above system context.
"""
    print("[LLM ask] Streaming prompt to Ollama model:", model)
    return call_ollama_stream(full_prompt, model=model)


def ask_followup(results, context=None, model=DEFAULT_OLLAMA_MODEL):
    """
    Ask the LLM for a follow-up question based on the user's prompt.
    Returns a single string response.
    """
    _, formatted_registry = read_model_registry(include_prompt_format=True)

    full_prompt = f"""
This is the results of your chosen tools:

{json.dumps(results, indent=2)}

Context features (non-tool signals):
{json.dumps(context or {}, indent=2)}

Based on this information, do you want to run other tools or are you satisfied with the current results?
If you want to run other tools, provide a JSON object with the list of tool names to run.

Available Tools:
{formatted_registry}

If you are satisfied with the current results, respond with a json "no"
like this:
```json
{{ "tools_to_run": ["no"] }}
``` 
If you want to run other tools, respond with a json like this:
```json
{{ "tools_to_run": ["gd_boost"] }}
```
    """
    raw_response = call_ollama(full_prompt, model=model)    
    print("[LLM follow-up] Response:", raw_response)
    try:
        json_text = extract_json_block(raw_response)
        print("[LLM follow-up] Parsed JSON:", json_text)
        parsed = json.loads(json_text)
        return parsed.get("tools_to_run", [])
    except Exception as e:
        print("[LLM follow-up] Error parsing response:", e)
        print("Full response:", raw_response)
        return ["no"]  # Default to no further tools

def say_error_stream(error, model=DEFAULT_OLLAMA_MODEL):
    """
    Returns a message indicating an error occurred in the LLM processing.
    """
    prompt = f"""
An error occurred while processing the user's request.
Error details: {error}
Please provide a user-friendly message indicating that an error occurred and suggest the user try again later.
"""
    try:
        # Consume the generator and join all streamed tokens into a single string
        response = call_ollama_stream(prompt, model=model)
        print("[LLM error] Response:", response)
        return response
    except Exception as e:
        print("[LLM error] Failed to get error message:", e)
        return "An unexpected error occurred. Please try again later."
