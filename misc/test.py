from helpers.conversational_agent import init_conversational_agent
from helpers.embedding_model import init_embedding_model
from helpers.vectorstore import create_vector_store, init_vectordb
from helpers.similarity_calculation import find_highest_similarity

from geopy.geocoders import Nominatim

# def setup_langchain_bot():
#     embedding_model = init_embedding_model()
#     init_vectordb()
#     vectorstore = create_vector_store(
#         "text", "langchain-retrieval-agent", embedding_model
#     )
#     agent = init_conversational_agent(vectorstore)
#     return agent, vectorstore

# agent, pinecone_vectorstore = setup_langchain_bot()

# incoming_msg = "What are some music events this weekend in Boston?"
# docs_and_scores = pinecone_vectorstore.similarity_search_with_score(incoming_msg)
# highest_similarity = find_highest_similarity(docs_and_scores)

# if '' in incoming_msg:
#     if highest_similarity >= 0.4:
#             response = agent(incoming_msg)
#             print("response:", response)

# print("similarity:", highest_similarity)

def location(lat, long):
    geolocator = Nominatim(user_agent="bot.py")
    coords = str(lat) + ", " + str(long)
    location = geolocator.reverse(coords, timeout = None)
    raw_location = location.raw['address']
    city_loc = raw_location['city'] + ", " + raw_location['state'] + ", " + raw_location['country']
    address_loc = raw_location['house_number'] + " " + raw_location['road'] + ", " + raw_location['city']
    return city_loc, address_loc

location()