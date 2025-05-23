"""
This module is used to get the weather data for a given location.
"""

from typing import Optional
from smolagents import CodeAgent, tool
from smolagents.models import OpenAIServerModel
from ranger.tools.maps import get_travel_duration
import logging

@tool
def get_weather(location: str) -> str:
    """Get a detailed weather report for a specific location.

    Args:
        location: The city or location to get weather information for.
                 Can be a city name, coordinates, or landmark.
                 Examples: "New York", "Paris, France", "Mount Everest"
    """
    logger = logging.getLogger(__name__)
    logger.debug("OpenAIServerModel in get_weather is %r", OpenAIServerModel)
    logger.debug("About to instantiate OpenAIServerModel with model_id='gpt-4'")
    model_instance = OpenAIServerModel(model_id="gpt-4")
    logger.debug("Instantiated OpenAIServerModel, got %r", model_instance)
    agent = CodeAgent(
        tools=[],
        model=model_instance,
        additional_authorized_imports=["datetime"]
    )
    
    response = agent.run(f"""
    Generate a realistic weather report for {location}. Include:
    - Temperature in Fahrenheit
    - Weather conditions (sunny, cloudy, rainy, etc.)
    - Humidity percentage
    - Wind speed in miles/hour
    
    Format the response in a clear, bullet-point style.
    """)
    
    return response 