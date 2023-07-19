from flask import Flask, request
import requests
import json
import subprocess
from twilio.twiml.messaging_response import MessagingResponse

from api_calls import post_pschat_message, getplaces_serp_api

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
    api_url = 'http://localhost:4000/'

@app.route('/bot', methods=['POST'])

def bot():

    user_phone_number = request.values.get('From')
    incoming_msg = request.values.get('Body','').lower()
    resp = MessagingResponse()
    msg = resp.message()
    
    response = None

    docs_and_scores = pinecone_vectorstore.similarity_search_with_score(incoming_msg)
    highest_similarity = find_highest_similarity(docs_and_scores)
    
    if highest_similarity >= 0.5:
        response = qabot.run(incoming_msg)

    elif "mile" in incoming_msg or "km" in incoming_msg:  ## to change soon
        response = getplaces_serp_api(incoming_msg)

    elif '' in incoming_msg:
        response = post_pschat_message(incoming_msg)

    msg.body(response)
    return str(resp)



if __name__ == '__main__':
    app.run(debug=True)





