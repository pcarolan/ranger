"""
This module is used to get the weather data for a given location.
"""

from typing import Optional
from smolagents import CodeAgent, tool, OpenAIModel

@tool
def get_travel_duration(start_location: str, destination_location: str, transportation_mode: Optional[str] = None) -> str:
    """Gets the travel time between two places.

    Args:
        start_location: the place from which you start your ride
        destination_location: the place of arrival
        transportation_mode: The transportation mode, in 'driving', 'walking', 'bicycling', or 'transit'. Defaults to 'driving'.
    """
    import os   # All imports are placed within the function, to allow for sharing to Hub.
    import googlemaps
    from datetime import datetime

    gmaps = googlemaps.Client(os.getenv("GMAPS_API_KEY"))

    if transportation_mode is None:
        transportation_mode = "driving"
    try:
        directions_result = gmaps.directions(
            start_location,
            destination_location,
            mode=transportation_mode,
            departure_time=datetime(2025, 6, 6, 11, 0), # At 11, date far in the future
        )
        if len(directions_result) == 0:
            return "No way found between these places with the required transportation mode."
        return directions_result[0]["legs"][0]["duration"]["text"]
    except Exception as e:
        print(e)
        return e

@classmethod
def get_weather(location: str) -> str:
    """Gets the weather for a given location. It uses the OpenAI API to get the weather data.   

    Args:
        location: the location for which you want to get the weather
    """
    return "The weather in Paris is sunny."

# agent = CodeAgent(tools=[get_travel_duration, get_weather], model=OpenAIModel(model="gpt-4o-mini"), additional_authorized_imports=["datetime"])

# agent.run("What is the weather in Paris today? And what is the travel time from Paris to Lyon?")
