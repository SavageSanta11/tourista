from api_calls import getplaces_google_local_api
import requests
import json

api_url = "http://localhost:4000"
api_request_headers  = {"Content-Type": "application/json"}
# used to generate 5 places for tour
# address = <number> <street>, <city>
# location = city, state, country
def generate_tour(address, location, user_phone_number):
    prompt = "attractions within a 1 mile radius of " + address
    places, coords_dict = getplaces_google_local_api(prompt, location)
    places_dict = {"places" : coords_dict[:5]}
    print(user_phone_number)
    place_update_response = requests.patch(
        f"{api_url}/api/users/{user_phone_number}/places",
        headers=api_request_headers,
        data=json.dumps(places_dict)
        )
    print(place_update_response)
    return places[:5], places_dict

#retrieves 1 place from top of user's list
def view_place(user_phone_number):
    user_places_response = requests.get(
        f"{api_url}/api/users/{user_phone_number}/places",
        headers=api_request_headers
        )
    return user_places_response.json()[0]

def tour_done(user_phone_number):
    user_places_response = requests.get(
        f"{api_url}/api/users/{user_phone_number}/places",
        headers=api_request_headers
        )
    return user_places_response.json() == []

def get_city(user_phone_number):
    return "Boston"

def remove_first(user_phone_number):
    get_place = requests.patch(
        f"{api_url}/api/users/{user_phone_number}/places/remove", 
        headers=api_request_headers
        )
    print(get_place)
    print(type(get_place))
    if get_place.status_code == 200:
        place_response = get_place.json()
        area_name = place_response["place"]["title"]
        return(area_name)
    else: return("error")