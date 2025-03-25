from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_openai import ChatOpenAI
from geopy.geocoders import Nominatim
import numpy as np
from itertools import permutations
from tools import *
import os
from sklearn.cluster import KMeans 

# Load Environment

with open(".env", "r") as f:
    for line in f:
        key, value = line.split("=")
        os.environ[key] = value.strip()

# LLM 

llm_tsp = ChatOpenAI(
  model="gpt-4o",
  temperature=0,
  verbose=True
)

# Get detail adress from web searchsearch

geolocator = Nominatim(user_agent="geo-app")


address_prompt = PromptTemplate(
    template="""You are an AI assistant that extract address information from the given text.
    You will receive a text containing address infomation, your job is to extract the following infomation into JSON format:
    Input: {place}
    Output:
    {{
        "address_1": "Địa chỉ chi tiết đầy đủ đường/ấp, phường/ xã, quận/ huyện, tỉnh/ thành phố",
        "address_2": "Địa chỉ gồm phường/ xã, quận/ huyện, tỉnh/ thành phố"
    }}

    """,
    input_variables=["place"]
)

address_chain = address_prompt | llm_tsp | JsonOutputParser()


def get_location(places, destination):
  location_list = []
  tavily_tool = TavilySearchResults(max_results=1)
  for place in places:
    print()
    address = tavily_tool.invoke(f"Địa chỉ chi tiết của {place} ở {destination}")
    if not isinstance(address, list):
        address = search_snippet(f"Địa chỉ chi tiết của {place} ở {destination}")
    else:
        address = address[0].get("content", "")
    location = address_chain.invoke({"place": address})

    loc = geolocator.geocode(location['address_1'], timeout=10)
    if loc is None:
        loc = geolocator.geocode(location['address_2'], timeout=10)
        location_list.append(
            {
                "place": place,
                "location": (loc.latitude, loc.longitude)
            }
        )
    else:
        location_list.append(
            {
                "place": place,
                "location": (loc.latitude, loc.longitude)
            }
        )

  return location_list

def euclidean(point1, point2):
    """Calculate the Euclidean distance between two points."""
    return np.sqrt(np.sum((np.array(point1) - np.array(point2)) ** 2))


def optimize_trip_with_hotel(hotel_location, destinations, daily_limit, distance_limit, travel_duration):
    """
    Optimize the travel itinerary, ensuring each cluster has at least `daily_limit` destinations.
    
    Args:
        hotel_location (tuple): Coordinates of the hotel (latitude, longitude).
        destinations (list): List of tuples representing the coordinates of the destinations (latitude, longitude).
        daily_limit (int): Minimum number of destinations to visit in one day.
        distance_limit (float): Maximum distance allowed for the trip in one day.
        travel_duration (int): Number of days available for travel.
    
    Returns:
        list: List of daily itineraries, each containing ordered destinations starting from the hotel.
    """
    def redistribute_clusters(clusters, daily_limit):
        for i, cluster in enumerate(clusters):
            if len(cluster) < daily_limit:
                for j, other_cluster in enumerate(clusters):
                    if i != j and len(other_cluster) > daily_limit:
                        cluster_center = np.mean(cluster, axis=0) if cluster else hotel_location
                        cluster_center = np.array(cluster_center)

                        other_cluster_distances = [
                            (point, euclidean(cluster_center, point)) for point in other_cluster
                        ]
                        other_cluster_distances.sort(key=lambda x: x[1])

                        while len(cluster) < daily_limit and other_cluster_distances:
                            closest_point, _ = other_cluster_distances.pop(0)
                            for idx, point in enumerate(other_cluster):
                                if np.array_equal(point, closest_point):
                                    del other_cluster[idx]
                                    break
                            cluster.append(closest_point)

        return clusters

    def nearest_neighbor_tsp(start, points):
        unvisited = points[:]
        current = start
        route = []
        total_distance = 0

        while unvisited:
            next_point = min(unvisited, key=lambda p: euclidean(current, p))
            distance_to_next = euclidean(current, next_point)
            
            if total_distance + distance_to_next > distance_limit:
                break
            
            route.append(next_point)
            unvisited = [point for point in unvisited if not np.array_equal(point, next_point)]
            total_distance += distance_to_next
            current = next_point

        return route

    hotel_location = np.array(hotel_location)
    destinations = [np.array(d) for d in destinations]

    kmeans = KMeans(n_clusters=travel_duration, random_state=42)
    labels = kmeans.fit_predict(destinations)

    clusters = [[] for _ in range(travel_duration)]
    for i, label in enumerate(labels):
        clusters[label].append(destinations[i])

    clusters = redistribute_clusters(clusters, daily_limit)

    itinerary = []
    for cluster in clusters:
        if cluster:
            ordered_route = nearest_neighbor_tsp(hotel_location, cluster)
            itinerary.append([hotel_location.tolist()] + [point.tolist() for point in ordered_route])

    return itinerary
def optimize_trip_with_hotel(hotel_location, destinations, daily_limit, distance_limit):
    """
    Optimize the travel itinerary starting from a fixed hotel location each day with a limit on total distance.

    Args:
        hotel_location (tuple): Coordinates of the hotel (latitude, longitude).
        destinations (list): List of tuples representing the coordinates of the destinations (latitude, longitude).
        daily_limit (int): Maximum number of destinations to visit in one day.
        distance_limit (float): Maximum distance allowed for the trip in one day.

    Returns:
        list: List of days, where each day is a list of destinations in optimal travel order starting from the hotel.
    """
    def tsp_solver_with_limit(start, points, distance_limit):
        """Solve the Traveling Salesman Problem starting from a fixed point with a distance limit."""
        best_order = []
        for perm in permutations(range(len(points))):
            distance = euclidean(start, points[perm[0]])
            valid = True
            for i in range(len(perm) - 1):
                distance += euclidean(points[perm[i]], points[perm[i+1]])
                if distance > distance_limit:
                    valid = False
                    break
            distance += euclidean(points[perm[-1]], start)  # Return to start point
            if valid and distance <= distance_limit:
                best_order = perm
                break
        return best_order

    # Step 1: Divide destinations into daily clusters
    num_days = -(-len(destinations) // daily_limit)  # Ceiling division
    clusters = [destinations[i:i+daily_limit] for i in range(0, len(destinations), daily_limit)]

    # Step 2: Optimize route within each cluster starting from the hotel
    itinerary = []
    for cluster in clusters:
        if len(cluster) > 0:
            order = tsp_solver_with_limit(hotel_location, cluster, distance_limit)
            ordered_cluster = [cluster[i] for i in order] if order else cluster
            itinerary.append([hotel_location] + ordered_cluster)

    return itinerary if itinerary else []

def optimize_distance_tour(destination, travel_duration, hotel, places, food, event):
    travel_duration = process_travel_duration(travel_duration)

    location_hotel = get_location([hotel], destination)
    location_places = get_location(places, destination)
    location_food = get_location(food, destination)
    location_event = get_location(event, destination)

    location_places = location_places + location_event + location_food

    start = location_hotel[0]["location"]
    places_map = {tuple(loc["location"]): loc["place"] for loc in location_places}  # Ensure keys are tuples

    places = list(places_map.keys())

    place_limit = 4
    distance_limit = 50

    itinerary_place = optimize_trip_with_hotel(start, places, place_limit, distance_limit)

    optimized_itinerary = []
    for day in range(travel_duration):
        day_trip = []
        if day < len(itinerary_place):
            day_trip.extend([places_map[tuple(loc)] for loc in itinerary_place[day][1:]])

        # Append the day trip to the final itinerary
        if day_trip:
            optimized_itinerary.append(day_trip)

    if not optimized_itinerary:
        return "Itinerary generation failed."
    else:
        itinerary_str = "\n".join(f"Ngày {day+1}: {', '.join(trip)}" for day, trip in enumerate(optimized_itinerary))
        print(itinerary_str)
        return itinerary_str


    