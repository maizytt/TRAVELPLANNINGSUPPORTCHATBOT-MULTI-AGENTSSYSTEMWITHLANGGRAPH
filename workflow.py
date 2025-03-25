# LangChain Dependencies
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_openai import ChatOpenAI

# For State Graph
from langgraph.graph import END, StateGraph
from typing import  Annotated, TypedDict, Literal


from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict
from langgraph.graph import StateGraph, add_messages, START, END
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from typing import TypedDict, Annotated, Sequence
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, END, MessagesState
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
import functools, operator

# For other module
from state import PlanTripState
from trip_info_team.graph import caller_app, trip_info_agent

from create_tour_team.agents  import *
from recommend_tour_team.agents import *

# ===================== Load Environment ===================

with open(".env", "r") as f:
    for line in f:
        key, value = line.split("=")
        os.environ[key] = value.strip()


load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')
os.environ["SERPER_API_KEY"] = os.getenv('SERPER_API_KEY')
os.environ["TAVILY_API_KEY"] = os.getenv('TAVILY_API_KEY')
os.environ['WEATHERMAP_API_KEY'] = os.getenv('WEATHERMAP_API_KEY')
os.environ["COHERE_API_KEY"] = os.getenv('COHERE_API_KEY')


llm = ChatOpenAI(
  model="gpt-4o-mini",
  temperature=0,
  verbose=True
)





# Router
llm_router = ChatOpenAI(model="gpt-4o", temperature=0)

input_router_1_prompt = PromptTemplate(
    template="""
    Your task is to analyze the user's request: "{input}".
    If the request is about suggesting or recommending tours, return "recommend".
    If the request is about creating or designing a tour, return "create".
    If the request belongs to other areas or is about searching for tour information, return "search".
    Only return one of the three values: "recommend", "create", or "search".

    Examples:
    - Input: "What is Hanoi?"
      Output: search

    - Input: "Can you suggest a tour to the USA for me?"
      Output: recommend

    - Input: "I want to create a tour to the USA"
      Output: create

    Current request:
    Input: "{input}"
    Output:
    """,
    input_variables=["input"]
)


def router_1(state: PlanTripState) -> Literal["recommend_tour_agent", "trip_info_agent", "create_tour_agent"]:
    evaluator = input_router_1_prompt | llm_router | StrOutputParser()
    message = state["messages"].content
    result = evaluator.invoke({"input": message})
    if result == "recommend":
        return "recommend_tour"

    elif result == "create":
        return "create_tour"

    else:
        return "search"
    

trip_workflow = StateGraph(PlanTripState)

trip_workflow.add_node("trip_info_agent", trip_info_agent)
trip_workflow.add_node("recommend_tour_agent", recommend_tour_agent)
trip_workflow.add_node("create_tour_agent", create_tour_agent)
trip_workflow.add_node("check_adjust", check_adjust)
trip_workflow.add_node("adjust_tour_agent", adjust_tour_agent)
trip_workflow.add_node("completion_tour_agent", completion_tour_agent)
trip_workflow.add_node("general_destination", general_destination_agent)



# Edges
trip_workflow.add_edge(START, "general_destination")
trip_workflow.add_conditional_edges(
    "general_destination",
    router_1,
    {
        "recommend_tour":"recommend_tour_agent",
        "search": "trip_info_agent",
        "create_tour": "create_tour_agent",
    },
)


trip_workflow.add_edge("recommend_tour_agent", "check_adjust")
trip_workflow.add_conditional_edges(
     "check_adjust",
    router_recommend_team,
    {
        "yes": "completion_tour_agent",
        "no": "create_tour_agent",
        "adjust": "adjust_tour_agent"
    },
)
trip_workflow.add_edge("adjust_tour_agent", "completion_tour_agent")
trip_workflow.add_edge("completion_tour_agent", END)
trip_workflow.add_edge("trip_info_agent", END)
trip_workflow.add_edge("recommend_tour_agent", END)


# Create Team

trip_workflow.add_node("accommodation_agent", accommodation_agent)
trip_workflow.add_node("event_agent", event_agent)
trip_workflow.add_node("places_agent", places_agent)
trip_workflow.add_node("food_agent", food_agent)
trip_workflow.add_node("transport_agent", transport_agent)
trip_workflow.add_node("generate_tour_agent", generate_tour_agent)
trip_workflow.add_node("price_agent", price_agent)

# Edges
trip_workflow.add_edge("create_tour_agent", "accommodation_agent")
trip_workflow.add_edge("accommodation_agent", "event_agent")
trip_workflow.add_edge("event_agent", "places_agent")
trip_workflow.add_edge("places_agent", "food_agent")
trip_workflow.add_edge("food_agent",  "transport_agent")
trip_workflow.add_edge("transport_agent",  "generate_tour_agent")
trip_workflow.add_edge("generate_tour_agent", "price_agent")
trip_workflow.add_edge("price_agent", END)

memory = MemorySaver()
trip_graph = trip_workflow.compile(checkpointer=memory, interrupt_before=["accommodation_agent"], interrupt_after=["check_adjust", "accommodation_agent","event_agent", "places_agent", "food_agent", "transport_agent"])


from IPython.display import Image, display

image_data = trip_graph.get_graph().draw_mermaid_png()
with open("graph_image.png", "wb") as f:
    f.write(image_data)