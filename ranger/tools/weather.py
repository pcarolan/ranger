"""
This module is used to get the weather data for a given location.
"""

from typing import Optional
from smolagents import CodeAgent, tool
from smolagents.models import OpenAIServerModel
from ranger.tools.maps import get_travel_duration

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
    - Wind speed in miles/hour
    
    Format the response in a clear, bullet-point style.
    """)
    
    return response 