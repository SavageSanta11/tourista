from flask import Flask, request
from googletrans import Translator
from spellchecker import SpellChecker
import random

from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from geopy.geocoders import Nominatim

from api_calls import post_pschat_message
from api_calls import weather_message

from helpers.conversational_agent import init_conversational_agent
from helpers.embedding_model import init_embedding_model
from helpers.vectorstore import create_vector_store, init_vectordb
from helpers.similarity_calculation import find_highest_similarity
from helpers.attraction import *

from googletrans import Translator

from helpers.list import similarity_score, preference_parsing, find_highest_sim, update_skip

from collections import deque
import queue

app = Flask(__name__)
translator = Translator()

api_url = "https://tourista-api-et6kobemta-ue.a.run.app"
api_request_headers  = {"Content-Type": "application/json"}

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
    location_populated = False
    user_interest_populated = False
    user_addresses = None
    user_lang = None
    user_phone_number = None
    spell = {"en": SpellChecker(), "es": SpellChecker('es'), "fr": SpellChecker("fr"), 
             "pt": SpellChecker('pt'), "de":SpellChecker('de'), "ru":SpellChecker('ru'),
              "ar":SpellChecker('ar'), "eu":SpellChecker('eu'), "lv":SpellChecker('lv') }
    #set up the chat history queue
    chat_history = []

def send_message(message):
    account_sid = 'AC37122a593e06653c42d235d0d83095cc'
    auth_token = 'd998865c8e9387ebe2aadb38c8b6e53e'
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        from_='whatsapp:+14155238886',
        body=message,
        to=user_phone_number
        )

def location(lat, long):
    geolocator = Nominatim(user_agent="bot.py")
    coords = str(lat) + ", " + str(long)
    try:
        location = geolocator.reverse(coords, timeout=None)
    except:
        return "", ""
    else:
        raw_location = location.raw["address"]
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

    
@app.route('/bot', methods=['POST'],)
def bot():
    #input info
    global user_interest_populated
    global location_populated
    global user_addresses
    global user_lang
    global chat_history
    global user_phone_number
    user_phone_number = request.values.get("From")
    incoming_msg = request.values.get('Body','').lower()
    longitude = request.values.get('Longitude','').lower()
    latitude = request.values.get('Latitude','').lower()
    resp = MessagingResponse()
    # msg = resp.message() 
    

    #spell-check for library supported languages
    try:
        if user_lang in ['en', 'es', 'fr', 'pt', 'de', 'ru', 'ar', 'eu', 'lv']:
            incoming_msg = " ".join(list(map((spell[user_lang]).correction, incoming_msg.split())))
    except Exception:
        pass
    
    response = None
    

    if incoming_msg and incoming_msg != "tour" and user_lang == None:
        detection = translator.detect(incoming_msg)
        #detect user language
        user_lang = (detection.lang).lower()
    
    trans_msg = translator.translate(incoming_msg, dest='en', src=(user_lang if user_lang else 'en')).text if incoming_msg else ""
    docs_and_scores = pinecone_vectorstore.similarity_search_with_score(trans_msg)
    highest_similarity = find_highest_similarity(docs_and_scores)
    print(highest_similarity)
    #print(trans_msg, "here", similarity_score("here", trans_msg))
    #PREFERENCE BRANCH
    #print("skip", trans_msg, similarity_score("skip_intent", trans_msg))
    if location_populated and not user_interest_populated:
    
        #we enter this branch if we need to populate the user's 
        preference = preference_parsing(trans_msg)
        chat_history.append("My preference is " + preference)
        five_attractions, loc_dict = generate_tour(user_addresses, user_phone_number, preference)
        
        
        if five_attractions == "error":
            response = "Invalid location or preference. Please try again."
        else:
            user_interest_populated = True

            chat_history.append( " , ".join(five_attractions))
    
            response = translator.translate("One moment! Generating your tour . . . ", dest = user_lang).text
        
        response = translator.translate(response, dest = user_lang if user_lang else 'en').text
        send_message(response)
            

        # creates + sends tour message
        tour_message = translator.translate("Here is a summary of your tour: \n", dest= user_lang).text
        for i in range(len(five_attractions)):
            tour_message += f"\n {i+1}. {five_attractions[i]}\n{loc_dict['places'][i]['coordinates']['street_address']}"
        tour_message += (
            "\n" + translator.translate("\n\n Follow this link for the footpath of the tour:", dest=user_lang).text
            + "\n" + str(maps_link(loc_dict, user_addresses))
        )
        tour_message += "\n\n" + translator.translate("Message me when you're at the first location and when you're ready for the next. Feel free to ask me for more information about a certain location!", dest= user_lang).text
        send_message(tour_message)
    
    # asks for location and processes location info
    # where MongoDB user object is populated
    #   list is generated by serpAPI or knowledge base/gpt
    #   user location from WhatsApp is stored   
    elif trans_msg == "tour":
        response = translator.translate("Hello, I am your virtual tour guide, Tourista!" , dest = user_lang if user_lang else 'en').text
        response = translator.translate(response, dest = user_lang if user_lang else 'en').text
    
        send_message(response)
        send_message("Please type HELLO in the langauge you would like to communicate in.")
        
    elif similarity_score("hello", trans_msg)>0.7:
        #store user language in MongoDB
        requests.post(f"{api_url}/api/users/{user_phone_number}/language", headers=api_request_headers, data=json.dumps({'language': user_lang}))
        response = "Before we start the tour, send your location! Press the + button on your keyboard to send us your pin!"
        response = translator.translate(response, dest = user_lang if user_lang else 'en').text
    
        send_message(response)
    elif latitude != "" and longitude != "":
        city_loc, address_loc = location(latitude, longitude)
        # catches error
        if city_loc == "" and address_loc == "":
            response = "Oh no! An error occurred. Please resend your location and wait a moment for your location to fully load before sending."
        # add user loction to MongoDB
        else:
            response = weather_message(latitude, longitude)
        response = translator.translate(response, dest = user_lang if user_lang else 'en').text
    
        send_message(response)

        user_loc = {
            "lat": float(latitude),
            "long": float(longitude),
            "street_address": address_loc,
        }
        user_addresses = {
            "lat": float(latitude),
            "long": float(longitude),
            "street_address": address_loc,
            "city_address": city_loc
        }
        user_update_location = requests.patch(
            f"{api_url}/api/users/{user_phone_number}/location",
            headers=api_request_headers,
            data=json.dumps({"location": user_loc}),
        )
        location_populated = True
        interest_prompt = "Please tell us about your interests so that we can tailor your experience to you. If you don't have a prefernce say NONE."
        send_message(translator.translate(interest_prompt, dest = user_lang).text)
            

    elif similarity_score('here', trans_msg) > 0.7:
        attraction = remove_first(user_phone_number)
        if(str(attraction) != "error"):
            here_init_str = "Awesome! Here are some fun facts about " + str(attraction) + "."
            area_query = "3 fun facts about" + str(attraction) + "in" + user_addresses["city_address"] + "in 2 sentences or less"
            doc_and_score = pinecone_vectorstore.similarity_search_with_score(area_query)
            higher_similarity = find_highest_similarity(doc_and_score)
            #print(higher_similarity)
            # ask chatgpt or knowledge base depending on similarity
            if higher_similarity >= 0.7:
                area_info = qabot.run(area_query)
            else:
                area_info = post_pschat_message(area_query)
            
            response = translator.translate(here_init_str, dest=user_lang, src='en').text
        
            send_message(response)
            
            # area_info_msg = resp.message()
            # next_prompt = resp.message()
            
            
            send_message(translator.translate(area_info, dest=user_lang, src='en').text)
            
            send_message(translator.translate("Ask me to go to the next location whenever you're ready!", dest = user_lang).text)
            
        else:
                tour_msg = "No more areas, but you can always start a new tour or chat with me."	
                send_message(translator.translate(tour_msg, dest = user_lang).text)
                user_interest_populated = False
                location_populated = False

    elif similarity_score("next", trans_msg)>0.7:
        
        if tour_done(user_phone_number):
            no_msg = "Your tour of " + get_city(user_phone_number) + " is complete! Thank you for using "	
            response = translator.translate(no_msg, dest = user_lang).text + " Tourista! " + translator.translate("Feel free to start a new tour with TOUR or ask me some questions.", dest = user_lang).text
            user_interest_populated = False
            location_populated = False
            response = translator.translate(response, dest = user_lang if user_lang else 'en').text
            send_message(response)
        else: 
            place = view_place(user_phone_number)
            title = place.get("title", "error")
            cords = place.get("coordinates", "")
            addr = cords.get("street_address", "")
            

            response_begin = ["Let's go to", "Head over to", "Make your way to", "Your next stop is", 
                                "The following location is", "Move towards", "Head towards"]
            response = f'{random.choice(response_begin)} {title}, {addr}'
            response = translator.translate(response, dest = user_lang if user_lang else 'en').text
            send_message(response)
            end_msg = 'Please let me know when you have arrived or if you want to end the tour.'
            send_message(translator.translate(end_msg, dest = user_lang if user_lang else 'en').text)
        
        
            # resp.message(translator.translate(end_msg, dest = user_lang).text)
    elif similarity_score("exit", trans_msg)>0.7:
        # clears places stack from MongoDB? clears user from mongoDB?
        response = "Okay! You may start a new tour with \"TOUR\" or ask me some questions."
        response = translator.translate(response, dest = user_lang if user_lang else 'en').text
        send_message(response)
        user_interest_populated = False
        location_populated = False

    # knowledge base functionality
    elif highest_similarity >= 0.45:
        #have the response include previous history as well as additoinal prompting for optimal answer
        response = qabot.run("Conversation history: " + str(chat_history) + "My question: " + trans_msg + ". Only answer the question, and if there is Conversation history only use if relevant. Summarize reponse in less than 4 sentences")
        response = translator.translate(response, dest = user_lang if user_lang else 'en').text
        send_message(response)
        #add the incoming message and the response to it to the chat history queue
        chat_history.append(trans_msg)
        chat_history.append(response)
    elif similarity_score("skip_intent", trans_msg) > 0.4:
        # print("skipped!")
        # print(str(similarity_score('skip places', trans_msg)) + " skipped score")
        gen_tour = view_places(user_phone_number)
        update_skip(gen_tour)
        # print(titles)
        # check the message against the places, highest similarity place gets taken out
        # print(similarity_score('skip places', trans_msg))

        if similarity_score('skip places', trans_msg) > 0.6:
            # find the specific place they mentioned
            index = find_highest_sim('skip places', trans_msg)
            # print(index)
            spec_place = str(gen_tour[index])
            new_spec = ''
            for char in spec_place:
                if char == " ":
                    new_spec += "%20"
                else:
                    new_spec += char
            # print("this is the place that is being requested " + new_spec)
            # remove the specific place
            remove_place(user_phone_number, new_spec)
            msg2 = f"Sounds good! {spec_place} has been removed from your itinerary."
            send_message(translator.translate(msg2, dest = user_lang).text)

            # print(len(view_places(user_phone_number)))
            if (len(view_places(user_phone_number)) >= 1):
                response = f"Your new itinerary: \n"
                for i, place in enumerate(view_places(user_phone_number), start=1):
                    response += f"\n{i}. {place}"
                    
            else:
                # print("this enters it being zero")
                response = "Congratulations! You have finished the tour. If you would like to start another tour, text TOUR!"

            send_message(translator.translate(response, dest = user_lang).text)
            # print(f"{api_url}/api/users/{user_phone_number}/places/remove/{new_spec}")
            # print("coming next is remaining tour list after removing specific place")
            # print(view_places(user_phone_number))
        
        else:
            response = "I'm sorry, that location is not in the itinerary."

    elif similarity_score('skip places', trans_msg) > 0.6:
        if similarity_score("skip_intent", trans_msg) > 0.3:
            print("skipped!")
            gen_tour = view_places(user_phone_number)
            update_skip(gen_tour)
            index = find_highest_sim('skip places', trans_msg)
            spec_place = str(gen_tour[index])
            new_spec = ''
            for char in spec_place:
                if char == " ":
                    new_spec += "%20"
                else:
                    new_spec += char
            remove_place(user_phone_number, new_spec)
            msg2 = f"Sounds good! {spec_place} has been removed from your itinerary."
            send_message(translator.translate(msg2, dest = user_lang).text)
            if (len(view_places(user_phone_number)) >= 1):
                response = f"Your new itinerary: \n"
                for i, place in enumerate(view_places(user_phone_number), start=1):
                    response += f"\n{i}. {place}"        
            else:
                response = "Congratulations! You have finished the tour. If you would like to start another tour, text TOUR!"
        else:
            response = post_pschat_message(incoming_msg)

        response = translator.translate(response, dest = user_lang if user_lang else 'en').text
        resume_msg = translator.translate("Please let me know if you want to resume the tour.", dest = user_lang if user_lang else 'en').text

        send_message(resume_msg)
        send_message(response)
    else:
        #have the response include previous history as well as additional prompting for optimal answer
        response = post_pschat_message("Conversation history: " + str(chat_history) + "My question: " + trans_msg +  ". Only answer the question in a cheerful tone, and if there is Conversation history only use if relevant. Summarize reponse in less than 4 sentences.")
        response = translator.translate(response, dest = user_lang if user_lang else 'en').text
        send_message(response)
        #add the incoming message and the response to it to the chat history queue
        chat_history.append(trans_msg)
        chat_history.append(response)
    
   
    # response = translator.translate(response, dest = user_lang if user_lang else 'en').text
    # msg.body(response)

    #turn the chat history into a queue 
    chat_history= deque(chat_history)
    #check if chat history length is above a certain length
    if len(chat_history) > 8:
        #remove oldest message of the conversation
        chat_history.popleft()
    #turn the chat history back into a queue 
    chat_history=list(chat_history)

    print(chat_history)

    return str(resp)

if __name__ == '__main__':
    app.run(port=5000)