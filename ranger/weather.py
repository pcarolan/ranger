"""
This module is used to get the weather data for a given location.
"""

from typing import Optional
from smolagents import CodeAgent, tool
from smolagents.models import OpenAIServerModel

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
        return str(e)

@tool
def get_weather(location: str) -> str:
    """Gets the weather for a given location using OpenAI to generate a realistic weather response.

    Args:
        location: the location for which you want to get the weather
    """
    agent = CodeAgent(
        tools=[],
        model=OpenAIServerModel(model_id="gpt-4"),
        additional_authorized_imports=["datetime"]
    )
    
    response = agent.run(f"""
    Generate a realistic weather report for {location}. Include:
    - Temperature in Fahrenheit
    - Weather conditions (sunny, cloudy, rainy, etc.)
    - Humidity percentage
    - Wind speed in km/h
    
    Format the response in a clear, bullet-point style.
    """)
    
    return response
