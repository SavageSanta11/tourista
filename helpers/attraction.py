from api_calls import getplaces_google_local_api
import requests
import json
# used to generate 5 places for tour
# address = <number> <street>, <city>
# location = city, state, country
def generate_tour(address, location, user_phone_number):
    prompt = "attractions within a 1 mile radius of " + address
    places, coords_dict = getplaces_google_local_api(prompt, location)
    api_url = "http://localhost:4000"
    api_request_headers  = {"Content-Type": "application/json"}
    places_dict = {"places" : coords_dict[:5]}
    print(user_phone_number)
    place_update_response = requests.patch(
        f"{api_url}/api/users/{user_phone_number}/places",
        headers=api_request_headers,
        data=json.dumps(places_dict)
        )
    print(place_update_response)
    return places[:5], places_dict