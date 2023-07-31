from api_calls import getplaces_google_local_api
from helpers.route_optimization import shortest_route
import requests
import json
import pyshorteners

api_url = "http://localhost:4000"
api_request_headers = {"Content-Type": "application/json"}


# used to generate (at most) 5 places for tour
# user_location = {'lat': <lat>, 'long': <long>, 'street_address': <address>}
# location = city, state, country
def generate_tour(location, user_location, user_phone_number, preference):
    if preference == "attractions":
        prompt = (
            "attractions within a 1 mile radius of " + user_location["street_address"]
        )
    else:
        prompt = preference + " near " + user_location["street_address"]
    places, coords_dict = getplaces_google_local_api(prompt, location)
    num_attractions = min(5, len(coords_dict))
    coords_dict = coords_dict[:num_attractions]
    user_dict = {}
    user_dict["title"] = "User location"
    user_dict["coordinates"] = {
        "latitude": user_location["lat"],
        "longitude": user_location["long"],
    }
    coords_dict.insert(0, user_dict)
    print(coords_dict)
    attraction_route = shortest_route(coords_dict)
    places_dict = {"places": attraction_route}
    place_update_response = requests.patch(
        f"{api_url}/api/users/{user_phone_number}/places",
        headers=api_request_headers,
        data=json.dumps(places_dict),
    )
    print(place_update_response)
    return [x["title"] for x in attraction_route], places_dict


# retrieves 1 place from top of user's list
def view_place(user_phone_number):
    user_places_response = requests.get(
        f"{api_url}/api/users/{user_phone_number}/places", headers=api_request_headers
    )
    return user_places_response.json()[0]


def tour_done(user_phone_number):
    user_places_response = requests.get(
        f"{api_url}/api/users/{user_phone_number}/places", headers=api_request_headers
    )
    return user_places_response.json() == []


def get_city(user_phone_number):
    return "Boston"


def remove_first(user_phone_number):
    get_place = requests.patch(
        f"{api_url}/api/users/{user_phone_number}/places/remove",
        headers=api_request_headers,
    )
    print(get_place)
    print(type(get_place))
    if get_place.status_code == 200:
        place_response = get_place.json()
        area_name = place_response["place"]["title"]
        return area_name
    else:
        return "error"


def maps_link(attractions_dict, user_location):
    google_url = "https://www.google.com/maps/dir/"
    user_coords = f"{user_location['lat']},{user_location['long']}"
    places = attractions_dict["places"]
    attraction_plus_arr = [x["title"].replace(" ", "+") for x in places]
    attractions_plus = ""
    for place in attraction_plus_arr:
        attractions_plus += place + "/"
    end_coords = f"@{places[-1]['coordinates']['latitude']},{places[-1]['coordinates']['longitude']},15z"
    # long_url = f"{google_url}{user_coords}/{attractions_plus}{end_coords}"
    long_url = f"{google_url}{user_coords}/{attractions_plus}"
    type_tiny = pyshorteners.Shortener()
    short_url = type_tiny.tinyurl.short(long_url)
    return short_url
