from haversine import haversine, Unit


def shortest_route(locations):
    final_route = []
    final_route.append(locations[0])
    while len(final_route) < 6:
        minimum = 2500
        place = final_route[-1]
        locations.remove(place)
        place_coords = (
            place["coordinates"]["latitude"],
            place["coordinates"]["longitude"],
        )
        for next_place in locations:
            next_place_coords = (
                next_place["coordinates"]["latitude"],
                next_place["coordinates"]["longitude"],
            )
            if haversine(place_coords, next_place_coords, unit=Unit.MILES) < minimum:
                minimum = haversine(place_coords, next_place_coords, unit=Unit.MILES)
                nearest = next_place
        final_route.append(nearest)
    return final_route[1:]


# locations = [
#     (42.3578, -71.0568), # current location
#     (42.3521821, -71.0512911),  # Location 1 Boston Tea Party Ships and Museum
#     (42.3587352,-71.05745399999999 ),  # Location 2 Old State House
#     (42.3550897, -71.0657256),  # Location 3 Boston Common
#     (42.363724999999995, -71.0536561),  # Location 4 Paul Revere House
#     (42.3592478, -71.0491475),  # Location 5 New England Aquarium
# ]


# optimized_route = shortest_route(locations)
# print(optimized_route)
