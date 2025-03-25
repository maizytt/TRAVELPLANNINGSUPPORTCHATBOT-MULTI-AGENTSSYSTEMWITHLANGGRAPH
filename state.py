from typing import TypedDict, Annotated
from pydantic import Field
from langchain_core.messages import HumanMessage


# Define the state object for the agent graph
class PlanTripState(TypedDict):
    # Input
    messages: Annotated[HumanMessage, Field(description="Human message")]
    user_inputs: dict

    # Process
    router_1_response: str
    recommend_chat: str
    adjust_choice: str
    tour_choice: list
    accommodation_query: str

    user_accommodation_choice: str
    user_event_choice: list
    user_places_choice: list
    user_food_choice: list
    user_transport_choice: str
    generate_tour_response: str

    # Ouput
    general_response: str
    ## Team Search
    trip_infor_response: str
    ## Team Recommend
    recommend_tour_response: list
    recommend_tour: str
    adjust_tour_response: str
    completion_tour_response: str
    ## Team Create
    event_response: str
    accommodation_response: str
    places_response: str
    food_response: str
    transport_response: str
    price_response: str
    generate_tour_response: str

