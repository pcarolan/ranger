"""
This module is used to get the weather data for a given location.
"""

from typing import Optional
from smolagents import CodeAgent, tool
from smolagents.models import OpenAIServerModel
from ranger.tools.maps import get_travel_duration

@tool
def get_weather(location: str) -> str:
    print(f"DEBUG: OpenAIServerModel in get_weather is {OpenAIServerModel!r}")
    print("DEBUG: About to instantiate OpenAIServerModel with model_id='gpt-4'")
    model_instance = OpenAIServerModel(model_id="gpt-4")
    print(f"DEBUG: Instantiated OpenAIServerModel, got {model_instance!r}")
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