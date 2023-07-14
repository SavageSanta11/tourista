from flask import Flask, request
import requests
import json
import subprocess
from twilio.twiml.messaging_response import MessagingResponse

from api_calls import post_pschat_message

from helpers.conversational_agent import init_conversational_agent
from helpers.embedding_model import init_embedding_model
from helpers.vectorstore import create_vector_store, init_vectordb
from helpers.similarity_calculation import find_highest_similarity

app = Flask(__name__)

def setup_langchain_bot():
    embedding_model = init_embedding_model()
    init_vectordb()
    vectorstore = create_vector_store(
        "text", "langchain-retrieval-agent", embedding_model
    )
    qabot = init_conversational_agent(vectorstore)
    return qabot, vectorstore

with app.app_context():
    qabot, pinecone_vectorstore = setup_langchain_bot()

@app.route('/bot', methods=['POST'])

def bot():
    incoming_msg = request.values.get('Body','').lower()
    resp = MessagingResponse()
    msg = resp.message()
    
    response = None

    docs_and_scores = pinecone_vectorstore.similarity_search_with_score(incoming_msg)
    highest_similarity = find_highest_similarity(docs_and_scores)

    if '' in incoming_msg:
        if highest_similarity >= 0.5:
            response = qabot.run(incoming_msg)

        elif '' in incoming_msg:
            response = post_pschat_message(incoming_msg)
    
    msg.body(response)
    return str(resp)



if __name__ == '__main__':
    app.run(port=4000)





