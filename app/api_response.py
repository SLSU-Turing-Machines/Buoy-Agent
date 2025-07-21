#------------------------
# Handles API responses and date formatting
#------------------------

import json
from datetime import datetime

def post_json(message):
    message["timestamp"] = datetime.now().isoformat()
    return json.dumps(message)  

def invalid_request():
    response = {"error": "Invalid request. Please provide a valid URL.", "timestamp": datetime.now().isoformat()}
    return json.dumps(response)  

def dataframe_response(df):
    response = df.to_dict(orient="records")
    for record in response:
        record["timestamp"] = datetime.now().isoformat()
    return json.dumps(response) 

def invalid_api_key():
    response = {"error": "Invalid API key. Please provide a valid key.", "timestamp": datetime.now().isoformat()}
    return json.dumps(response) 
