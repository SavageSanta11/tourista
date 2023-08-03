from haversine import haversine, Unit
from api_calls import getplaces_google_local_api

def shortest_route(locations):
    final_route = []
    final_route.append(locations[0])
    num_stops = len(locations)
    i = 0
    while len(final_route) < num_stops:
        minimum = 24000
        place = final_route[-1]
        locations.remove(place)
        place_coords = (place['coordinates']['latitude'],
                        place['coordinates']['longitude'])
        for next_place in locations:
            next_place_coords = (next_place['coordinates']['latitude'],
                                 next_place['coordinates']['longitude'])
            if haversine(place_coords, next_place_coords, unit=Unit.MILES) < minimum:
                minimum = haversine(place_coords, next_place_coords, unit=Unit.MILES)
                nearest = next_place
        final_route.append(nearest)
    return final_route[1:]