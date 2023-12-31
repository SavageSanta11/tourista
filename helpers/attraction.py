from api_calls import getplaces_google_local_api
from helpers.route_optimization import shortest_route
import requests
import json

api_url = "http://localhost:4000"
api_request_headers  = {"Content-Type": "application/json"}
# used to generate 5 places for tour
# address = <number> <street>, <city>
# location = city, state, country
def generate_tour(location, user_location, user_phone_number):
    prompt = "attractions within a 1 mile radius of " + user_location['street_address']
    places, coords_dict = getplaces_google_local_api(prompt, location)
    num_attractions = min(5, len(coords_dict))
    coords_dict = coords_dict[:num_attractions]
    user_dict = {}
    user_dict['title'] = "User location"
    user_dict['coordinates'] = {'latitude': user_location['lat'], 'longitude': user_location['long']}
    coords_dict.insert(0, user_dict)
    attraction_route = shortest_route(coords_dict)
    places_dict = {"places" : attraction_route}
    place_update_response = requests.patch(
        f"{api_url}/api/users/{user_phone_number}/places",
        headers=api_request_headers,
        data=json.dumps(places_dict)
        )
    #print(place_update_response)
    return [x['title'] for x in attraction_route], places_dict

#retrieves 1 place from top of user's list
def view_place(user_phone_number):
    user_places_response = requests.get(
        f"{api_url}/api/users/{user_phone_number}/places",
        headers=api_request_headers
        )
    return (user_places_response.json()[0])

def get_city(user_phone_number):
    user_city_response = requests.get(f"{api_url}/api/users/{user_phone_number}/location", headers=api_request_headers)
    user_loc = user_city_response.json()
    return ((user_loc.get('street_address', 'Boston, MA')).split(",")[1]).strip()
#checks whether user has more places to visit
def tour_done(user_phone_number):
    user_places_response = requests.get(
        f"{api_url}/api/users/{user_phone_number}/places",
        headers=api_request_headers
        )
    return user_places_response.json() == []

#removes first place from user's list
def remove_first(user_phone_number):
    get_place = requests.patch(
        f"{api_url}/api/users/{user_phone_number}/places/remove", 
        headers=api_request_headers
        )
    #print(get_place)
    #print(type(get_place))
    if get_place.status_code == 200:
        place_response = get_place.json()
        area_name = place_response["place"]["title"]
        return(area_name)
    else: return("error")

def maps_link(attractions_dict, user_location):
    google_url = 'https://www.google.com/maps/dir/'
    user_coords = f"{user_location['lat']},{user_location['long']}"
    places = attractions_dict['places']
    attraction_plus_arr = [x['title'].replace(" ", "+") for x in places]
    attractions_plus = ''
    for place in attraction_plus_arr:
        attractions_plus += (place + '/')
    end_coords = f"@{places[-1]['coordinates']['latitude']},{places[-1]['coordinates']['longitude']},15z"
    link = f"{google_url}{user_coords}/{attractions_plus}{end_coords}"
    return link
