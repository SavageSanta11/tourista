import os
from flask import Flask, request, abort
import requests
import json
from twilio.request_validator import RequestValidator
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)


@app.route('/', methods=['POST'])
def reset():
    incoming_msg = request.values.get('Body','').lower()
    resp = MessagingResponse()
   
    headers = {
        "Authorization": "Bearer YOUR_PSCHAT_KEY",
        "Content-Type": "application/json"
        } 
    url = "https://api.psnext.info/api/chat"
    data = {
        "message": incoming_msg,
        "options": {
            "model": "gpt35turbo"
        }
    }
  
    if '' in incoming_msg:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        data = response.json()
        content = data['data']['messages'][2]['content']
    

        resp.message(content)      
    return str(resp), 200, {'Content-Type': 'application/xml'}