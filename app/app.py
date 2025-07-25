#  
#  _   _             
# | | | |            
# | |_| |_ _ __ ___  
# | __| __| '_ ` _ \ 
# | |_| |_| | | | | |
#  \__|\__|_| |_| |_|
#                   
# ------------------------------------------
# This file contains the main Flask application that serves as the API server for the phishing detection model. 
# The server is responsible for handling incoming requests, extracting features from the input URL, 
# tokenizing the URL, and making predictions using the trained model. 
#
# The server also implements an API key system to authenticate requests and ensure that only authorized users can access the prediction service. 
# The server is designed to run on a specific port and can be accessed by sending POST requests to the specified endpoint.
# The default port is 8050 and will run on localhost.
# ------------------------------------------

import asyncio
import sys
import dill
from flask import Flask, request, Response, jsonify
from flask_cors import CORS
import pandas as pd
import os
import api_response as ar
import extract_feature as ef
import ttm_tokenizer as ttmt
import numpy as np
import json
import time
import warnings

from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from pytorch_tabnet.tab_model import TabNetClassifier
import xgboost as xgb

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.llm_agent import stream_explanation_verdict, choose_tools, ask_llm, ask_followup, say_error_stream, extract_json_block
from agent.get_context_features import get_context_features

from agent.tools.base_model import BaseModel
from agent.tools.gd_boost_tool import GradientBoostingModel
from agent.tools.knn_tool import KNNModel
from agent.tools.rand_forest_tool import RandomForestModel
from agent.tools.svm_tool import SVMModel
from agent.tools.tabnet_tool import TabNetModel
from agent.tools.load_scaler import LoadScaler

from call_icp import fetch_from_icp

from urllib.parse import unquote
import re
import dotenv

dotenv.load_dotenv()  # Load environment variables from .env file

warnings.filterwarnings("ignore")


print("Server is starting...")

api_key = dotenv.get_key(".env", "buoy")
print("Generated API key:", api_key)
print("API key loaded")

# API Key Dictionary
API_KEYS = {"admin": api_key}
print("API keys:", API_KEYS)

def validate_api_key(api_key):
    return api_key in API_KEYS.values()

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins="*", allow_headers=["*"])  # Allow all headers

# Load individual model components
scaler = LoadScaler("model/scaler.pkl")

base_model = BaseModel("model/ttm_phishing_pipeline.pkl")
gd_boost_tool = GradientBoostingModel("model/gradientboosting_model.pkl")
knn_tool = KNNModel("model/knn_model.pkl")
rand_forest_tool = RandomForestModel("model/randomforest_model.pkl")
svm_tool = SVMModel("model/svm_model.pkl")
tabnet_tool = TabNetModel("model/tabnet_model.zip")

# ------------------------------
# Function to extract URLs from text
# ------------------------------
def extract_urls_from_text(text):
    """Extract URLs from text using regex patterns"""
    # Enhanced URL pattern to catch various formats
    url_patterns = [
        r'https?://(?:www\.)?[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?',  # Full URLs with optional www and path
        r'www\.[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?',                # www URLs
        r'[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?'                      # domain.com, sub.domain.org/path
    ]

    
    urls = []
    for pattern in url_patterns:
        found_urls = re.findall(pattern, text, re.IGNORECASE)
        urls.extend(found_urls)
    
    # Clean and normalize URLs
    normalized_urls = []
    for url in urls:
        url = url.strip('.,!?;')  # Remove trailing punctuation
        if not url.startswith(('http://', 'https://')):
            if url.startswith('www.'):
                url = 'https://' + url
            elif '.' in url:  # Assume it's a domain
                url = 'https://' + url
        normalized_urls.append(url)
    
    return normalized_urls

# ------------------------------
# Function to handle chatbot responses for non-URL messages
# ------------------------------
def handle_chatbot_response(message):
    """Handle general chatbot messages without URLs using streaming"""

    def generate():
        try:
            # Initial placeholder while model is loading
            initial_event = json.dumps({
                "status": "Thinking...",
                "response": "...",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
            })
            yield f"data: {initial_event}\n\n"

            # Stream actual LLM response chunks
            for chunk in ask_llm(message, model="gemma2:2b"):
                event = json.dumps({
                    "status": "buoy_response",
                    "response": chunk,
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
                })
                yield f"data: {event}\n\n"

            # Completion message
            completion_event = json.dumps({
                "status": "Done",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
            })
            yield f"data: {completion_event}\n\n"

        except Exception as e:
            # Error event
            error_event = json.dumps({
                "status": "error",
                "response": {
                    "type": "error",
                    "message": f"Error generating response: {str(e)}"
                },
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
            })
            yield f"data: {error_event}\n\n"

    return Response(generate(), mimetype="text/event-stream")

# ------------------------------
# Function to handle phishing prediction with SSE response
# ------------------------------
def predict_url_phishing(input_url, ef, ttmt, model="gemma2:2b"):
    print("Received URL:", input_url)

    def generate():
        headers = {'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache'}

        def send_event(status, response=None):
            event = json.dumps({"status": status, "response": response, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")})
            return f"data: {event}\n\n"

        # Validate URL format
        if not re.match(r'https?://', input_url):
            yield send_event("Error: Invalid URL format. Please provide a complete URL starting with http:// or https://")
            return

        # Fetch webpage details
        yield send_event("Fetching webpage details...")
        try:
            html_content = asyncio.run(fetch_from_icp(input_url))
            web_desc = ef.get_web_desc(input_url, html_content)
            if not isinstance(web_desc, dict):
                yield send_event("Error: Unable to fetch webpage details. The URL might be inaccessible.")
                return
        except Exception as e:
            yield send_event(f"Error: Failed to fetch webpage: {str(e)}")
            return

        df = pd.DataFrame([web_desc])
        
        results = {}

        # Tokenizing URL
        yield send_event("Tokenizing URL...")
        try:
            df = ttmt.tokenize(df)
        except Exception as e:
            yield send_event(f"Error: Failed to tokenize URL: {str(e)}")
            for line in say_error_stream(e, model=model):
                    yield send_event("buoy_response", line)
            return


        # Let LLM decide which tools to run
        yield send_event("Consulting AI for analysis strategy...")
        try:
            tools_to_run = choose_tools(input_url, model=model)
        except Exception as e:
            print(f"Tool selection failed: {e}")
            tools_to_run = ["base_model"]  # Fallback to base_model only

        yield send_event(f"Selected tools: {', '.join(tools_to_run)}")
        for tool in tools_to_run:
            yield send_event(f"Running {tool}...")
            try:
                results[tool] = call_tool(tool, df)
            except Exception as e:
                yield send_event(f"{tool} analysis failed: {str(e)}")

        # Add context features
        yield send_event("Gathering additional context...")
        try:
            context = get_context_features(input_url)

            context = {**context,
                "redirection_chain": df.get("redirection_chain", [None])[0],
                "ip_address": df.get("ip_address", [None])[0],
                "country": df.get("country", [None])[0],
                "certificate": df.get("certificate", [None])[0],
                "description": df.get("description", [None])[0],
                "hosting_provider": df.get("hosting_provider", [None])[0],
                "abuse_contact": df.get("abuse_contact", [None])[0],
            }

            print("[Context features] Extracted context:", context)
        except Exception as e:
            print(f"Context gathering failed: {e}")
            context = {}

        print("[Results] Final results:", results)

        #asking for follow-up questions
        yield send_event("Asking AI for evaluation and follow-up analysis...")
        generate_analysis = False
        followup_attempts = 0  # Counter to limit follow-up rounds

        while not generate_analysis and followup_attempts < 3:
            try:
                followup_tools = ask_followup(results, context, model=model)
                print("[LLM follow-up] Tools:", followup_tools)
                followup_attempts += 1

                if followup_tools:
                    for tool in followup_tools:
                        yield send_event(f"Running follow-up tool: {tool}")
                        if tool == "no":
                            generate_analysis = True
                            break

                        tool_result = call_tool(tool, df)
                        if tool_result is not None:
                            results[tool] = tool_result
                        else:
                            yield send_event(f"{tool} returned no result.")

            except Exception as e:
                print("[LLM follow-up] Error:", e)
                break


        # Stream LLM explanation
        yield send_event("Generating AI analysis report...")
        llm_verdict = ""
        try:
            for line in stream_explanation_verdict(results, context, model=model):
                llm_verdict += line  # accumulate stream into one string
                yield send_event("AI Analysis", line)
        except Exception as e:
            yield send_event("AI Analysis", f"Analysis completed with limited explanation due to: {str(e)}")

        # Fallback response, else fallback
        fallback_result = results.get("base_model") or {
            "verdict": "Unknown",
            "probabilities": {"phishing": 0.0, "legit": 0.0}
        }

        # Attempt to extract JSON from accumulated stream
        llm_verdict = extract_json_block(llm_verdict) 
        # turn {"verdict": "phishing"} into "phishing"
        if llm_verdict:
            try:
                llm_verdict = json.loads(llm_verdict).get("verdict", "Unknown")
            except json.JSONDecodeError:
                llm_verdict = "Unknown"

        response_payload = {
            "url": input_url,
            "predicted_class": llm_verdict or fallback_result["verdict"],
            "confidence_phishing": fallback_result["probabilities"]["phishing"],
            "confidence_legit": fallback_result["probabilities"]["legit"],
            "tools_used": list(results.keys()),
            "redirection_chain": df.get("redirection_chain", [None])[0],
            "ip_address": df.get("ip_address", [None])[0],
            "country": df.get("country", [None])[0],
            "certificate": df.get("certificate", [None])[0],
            "description": df.get("description", [None])[0],
            "hosting_provider": df.get("hosting_provider", [None])[0],
            "abuse_contact": df.get("abuse_contact", [None])[0],
        }

        yield send_event("Done", response_payload)

    return Response(generate(), mimetype="text/event-stream")

def call_tool(tool_name, df):
    """
    Call the specified tool with the provided input data.
    Returns the result of the tool's operation.
    """
    # Define model features
    xgboost_features = [
        'has_ip', 'has_https', 'url_tokens_0', 'url_tokens_1', 
        'hostname_tokens_0', 'hostname_tokens_1', 'hostname_tokens_2', 'certificate_tokens_0',
        'sensitive_word', 'url_length', 'url_entropy', 'ratio_char_digit'
    ]
    html_features = ['html_tokens_0', 'html_tokens_1', 'html_tokens_2', 'html_tokens_3', 'html_tokens_4', 'html_tokens_5']

    tool_features = [
        "has_ip", "has_https", 
        "url_tokens_0", "url_tokens_1",
        "hostname_tokens_0", "hostname_tokens_1", "hostname_tokens_2", 
        "html_tokens_0", "html_tokens_1", "html_tokens_2", "html_tokens_3",
    ]

    # Feature extraction
    print("Extracting features...")
    try:
        x_xgb_sample = df[xgboost_features].values
        x_html_sample = df[html_features].values
        tool_features_sample = scaler.run(df[tool_features].values)
    except KeyError as e:
        print(f"Error: Missing required features: {str(e)}")
        return None

    # Tool dispatch with error handling for all available models

    if tool_name == "base_model":
        try:
            return base_model.run(x_xgb_sample, x_html_sample)
        except Exception as e:
            print(f"Base model analysis failed: {str(e)}")
            return None

    if tool_name == "gd_boost":
        try:
            return gd_boost_tool.run(tool_features_sample)
        except Exception as e:
            print(f"Gradient Boosting analysis failed: {str(e)}")
            return None

    if tool_name == "knn":
        try:
            return knn_tool.run(tool_features_sample)
        except Exception as e:
            print(f"KNN analysis failed: {str(e)}")
            return None

    if tool_name == "rand_forest":
        try:
            return rand_forest_tool.run(tool_features_sample)
        except Exception as e:
            print(f"Random Forest analysis failed: {str(e)}")
            return None

    if tool_name == "svm":
        try:
            return svm_tool.run(tool_features_sample)
        except Exception as e:
            print(f"SVM analysis failed: {str(e)}")
            return None

    if tool_name == "tabnet":
        try:
            return tabnet_tool.run(tool_features_sample)
        except Exception as e:
            print(f"TabNet analysis failed: {str(e)}")
            return None

    # Unknown tool fallback
    print(f"Unknown tool name '{tool_name}' provided.")
    return None

def load_model(model_path="./model/ttm_phishing_pipeline.pkl"):
    try:
        with open(model_path, "rb") as f:
            model = dill.load(f, ignore=False)
        print("Model loaded successfully.")
        return model
    except FileNotFoundError:
        print(f"Error: Model file not found at {model_path}.")
        raise
    except dill.UnpicklingError:
        print("Error: Failed to load the model. The file may be corrupted or incompatible.")
        raise
    except Exception as e:
        print(f"An unexpected error occurred while loading the model: {e}")
        raise
# ------------------------------
# API Route: POST /buoy (Phishing Detection)
# ------------------------------

@app.before_request
def handle_preflight():
    print("Handling preflight request...")
    if request.method == "OPTIONS":
        response = Response()
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response, 200

@app.route("/buoy", methods=["POST"])
def buoy():
    print("Received request...")
    
    # Validate API key
    api_key = request.headers.get("X-API-KEY")
    if not validate_api_key(api_key):
        return ar.invalid_api_key()

    try:
        data = request.get_json()
        if not data:
            return ar.invalid_request()
    except Exception as e:
        return ar.invalid_request()

    # Get model preference
    model = data.get("model", "gemma2:2b")
    
    # Method 1: Direct URL provided
    input_url = data.get("url")
    
    if input_url:
        print(f"Direct URL provided: {input_url}")
        return predict_url_phishing(input_url, ef, ttmt, model=model)
    
    # Method 2: Extract URL from message/text
    message = data.get("message", "")
    text = data.get("text", message)  # Support both 'message' and 'text' fields
    
    if text:
        print(f"Analyzing text for URLs: {text[:100]}...")
        
        # Extract URLs from the text
        urls_found = extract_urls_from_text(text)
        
        if urls_found:
            # Use the first URL found
            selected_url = urls_found[0]
            print(f"URL extracted from text: {selected_url}")
            
            # Provide feedback about URL selection if multiple URLs found
            if len(urls_found) > 1:
                print(f"Multiple URLs found, analyzing the first one: {selected_url}")
            
            return predict_url_phishing(selected_url, ef, ttmt, model=model)
        else:
            # No URLs found - handle as chatbot interaction
            print("No URLs found in message, providing chatbot response")
            return handle_chatbot_response(text)
    
    # No valid input provided
    return ar.invalid_request()

# ------------------------------
# Health check endpoint
# ------------------------------
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy as a shark",
        "service": "buoy-phishing-detection-api",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
    })

# ------------------------------
# Main Entry Point
# ------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    print(f"Starting server on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)