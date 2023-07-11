from flask import Flask, request
import requests
import json
import subprocess
from twilio.twiml.messaging_response import MessagingResponse

from embedding_model import init_embedding_model
from vectorstore import init_vectordb, create_vector_store
from conversational_agent import init_conversational_agent

def setup_langchain_bot():
    embedding_model = init_embedding_model()
    init_vectordb()
    vectorstore = create_vector_store("text", "langchain-retrieval-agent", embedding_model)
    qabot = init_conversational_agent(vectorstore)
    return qabot

app = Flask(__name__)

@app.route('/bot', methods=['POST'])

def bot():
    incoming_msg = request.values.get('Body','').lower()
    resp = MessagingResponse()
    msg = resp.message()
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJVc2VySW5mbyI6eyJpZCI6MjE0MTgsInJvbGVzIjpbImRlZmF1bHQiXSwicGF0aWQiOiIzYjhlZDlkMS01ZjQxLTQ5MWEtOThiMS0wY2M0ZTVhZDcyOGUifSwiaWF0IjoxNjg4NjUxMjA5LCJleHAiOjE2OTM4MzUyMDl9.NyiRQPm9Fsv3HtYz_SmW-OI4Qe60Na0w4ytMJ6zi6aA",
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
        msg.body(content)

    return str(resp)



if __name__ == '__main__':
    #qabot = setup_langchain_bot()
    app.run(debug=True, port=4000)

