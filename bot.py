from flask import Flask, request

# from googletrans import Translator
import random

from twilio.twiml.messaging_response import MessagingResponse
from geopy.geocoders import Nominatim

from api_calls import post_pschat_message
from api_calls import weather_message

from helpers.conversational_agent import init_conversational_agent
from helpers.embedding_model import init_embedding_model
from helpers.vectorstore import create_vector_store, init_vectordb
from helpers.similarity_calculation import find_highest_similarity
from helpers.attraction import *
from helpers.list import similarity_score


app = Flask(__name__)
# translator = Translator()


def setup_langchain_bot():
    embedding_model = init_embedding_model()
    init_vectordb()
    vectorstore = create_vector_store(
        "text", "langchain-retrieval-agent", embedding_model
    )
    qabot = init_conversational_agent(vectorstore)
    return qabot, vectorstore


def location(lat, long):
    geolocator = Nominatim(user_agent="bot.py")
    coords = str(lat) + ", " + str(long)
    location = geolocator.reverse(coords, timeout=None)
    raw_location = location.raw["address"]
    print(raw_location)
    # checking house num
    if "house_number" in raw_location:
        house_number = raw_location["house_number"]
    else:
        house_number = ""
    # checking city/town
    if "city" in raw_location:
        city = raw_location["city"]
    elif "town" in raw_location:
        city = raw_location["town"]
    else:
        city = ""
    # checking road
    if "road" in raw_location:
        road = raw_location["road"]
    else:
        road = ""
    # check state
    if "state" in raw_location:
        state = raw_location["state"]
    else:
        state = ""
    # check country
    if "country" in raw_location:
        country = raw_location["country"]
    else:
        country = ""

    city_loc = city + ", " + state + ", " + country
    address_loc = house_number + " " + road + ", " + city
    return city_loc, address_loc


with app.app_context():
    qabot, pinecone_vectorstore = setup_langchain_bot()


@app.route("/bot", methods=["POST"])
def bot():
    user_phone_number = request.values.get("From")
    incoming_msg = request.values.get("Body", "").lower()
    longitude = request.values.get("Longitude", "").lower()
    latitude = request.values.get("Latitude", "").lower()
    resp = MessagingResponse()
    msg = resp.message()

    response = None
    data = None
    # similarity search for knowledge base
    docs_and_scores = pinecone_vectorstore.similarity_search_with_score(incoming_msg)
    highest_similarity = find_highest_similarity(docs_and_scores)

    # TRANSLATION
    # detection = translator.detect(incoming_msg)
    # #detects user lang
    # user_lang = detection.lang.lower()
    # # translates user msg into english
    # trans_msg = translator.translate(incoming_msg, dest = "en").text
    # print(trans_msg)

    # TOUR
    if similarity_score("tour", incoming_msg) > 0.7:
        response = "Hello, I am your virtual tour guide, Tourista! Please type HELLO in the langauge you would like to communicate in."

    # HELLO for tour
    elif similarity_score("hello", incoming_msg) > 0.7:
        print("inside hello")
        response = "Before we start the tour, send your location! Press the + button on your keyboard to send us your pin!"
        # print langauge in the console to check this response

    # LOCATION sent
    elif latitude != "" and longitude != "":
        # city_loc = "<city>, <state>, <country>"
        # address_loc = "<number> <street>, <city>"
        city_loc, address_loc = location(latitude, longitude)
        # add user loction to MongoDB
        user_loc = {
            "lat": float(latitude),
            "long": float(longitude),
            "street_address": address_loc,
        }
        api_url = "http://localhost:4000"
        api_request_headers = {"Content-Type": "application/json"}
        user_update_location = requests.patch(
            f"{api_url}/api/users/{user_phone_number}/location",
            headers=api_request_headers,
            data=json.dumps({"location": user_loc}),
        )
        preference = "attractions"
        # generates 5 places for tour
        # format - loc_dict = {'places':
        # [{'title': <title>, 'coordinates' :
        # {'latitude': <latitude>, 'longitude': <longitude>, 'street_address': <num street>}}]}
        five_attractions, loc_dict = generate_tour(
            city_loc, user_loc, user_phone_number, preference
        )
        response = weather_message(latitude, longitude)
        resp.message("One moment! Generating your tour . . . ")
        tour_message = "Here is a summary of your tour: \n"
        # creates + sends tour message
        for i in range(len(five_attractions)):
            tour_message += f"\n {i+1}. {five_attractions[i]}\n{loc_dict['places'][i]['coordinates']['street_address']}"
        tour_message += "\n\n Follow this link for the footpath of the tour: \n" + str(
            maps_link(loc_dict, user_loc)
        )
        tour_message += "\n\n Message me when you're at the location and when you're ready for the next. Feel free to ask me for more information about a certain location!"
        resp.message(tour_message)

    # HERE
    # pops location from MongoDB
    # gives info about this location using knowledge base/gpt
    elif similarity_score("here", incoming_msg) > 0.7:
        attraction = remove_first(user_phone_number)
        if str(attraction) != "error":
            response = (
                "Awesome! Finding some fun facts about "
                + str(attraction)
                + " for you..."
            )
            area_query = "3 fun facts about" + str(attraction)
            doc_and_score = pinecone_vectorstore.similarity_search_with_score(
                area_query
            )
            higher_similarity = find_highest_similarity(doc_and_score)
            # ask chatgpt or knowledge base depending on similarity
            if higher_similarity >= 0.5:
                area_info = qabot.run(area_query)
            else:
                area_info = post_pschat_message(area_query)
            resp.message(area_info)
            msg2 = resp.message()
            msg2.body("Ask me to go to the next location whenever you're ready!")
        else:
            response = (
                "No more areas, but you can always start a new tour or chat with me."
            )

    # NEXT
    # views next from MongoDB, sends to user
    elif similarity_score("next", incoming_msg) > 0.7:
        if tour_done(user_phone_number):
            response = f"Your tour of {get_city(user_phone_number)} is complete! Thank you for using Tourista!"
        else:
            place = view_place(user_phone_number)
            cords = place.get("coordinates", "")
            place_lon = cords.get("longitude", 0.0)
            place_lat = cords.get("latitude", 0.0)
            geolocator = Nominatim(user_agent="bot.py")
            cords = str(place_lat) + ", " + str(place_lon)
            attract_loc = geolocator.reverse(cords, timeout=None)
            response_begin = [
                "Let's go to",
                "Head over to",
                "Make your way to",
                "Your next stop is",
                "The following location is",
                "Move towards",
                "Head towards",
            ]
            response = f"{random.choice(response_begin)} {attract_loc.address}"

            # # map_msg = Message()
            # # map_msg.media(f'https://www.google.com/maps/search/?api=1&query={place_lat},{place_lon}')
            # # map_msg.body(attract_loc.address)
            # resp.append(map_msg)
            resp.message(
                "Please let me know when you have arrived or if you want to end the tour."
            )

    # CHATBOT ONLY - knowledge base
    elif highest_similarity >= 0.5:
        response = qabot.run(incoming_msg)

    # CHATBOT ONLY - chatgpt
    else:
        response = post_pschat_message(incoming_msg)

    # response = translator.translate(response, dest = user_lang).text
    msg.body(str(response))

    print(response)

    return str(resp)


if __name__ == "__main__":
    app.run(port=5000)

    # if latitude != "" and longitude != "":
    #     city_loc, address_loc = location(latitude, longitude)
    #     user_loc = {'latitude': float(latitude), 'longitude': float(longitude)}
    #     five_attractions, loc_dict = generate_tour(address_loc, city_loc, user_loc, user_phone_number)
    #     response = five_attractions
    #     maps_link(loc_dict, user_loc)
