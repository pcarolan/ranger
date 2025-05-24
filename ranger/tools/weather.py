"""
This module is used to get the weather data for a given location.
"""

import logging
from smolagents import CodeAgent, tool
from smolagents.models import OpenAIServerModel
from ranger.models.claude import ClaudeServerModel

logger = logging.getLogger(__name__)


@tool
def get_weather(location: str, model_type: str = "claude") -> str:
    """Get a detailed weather report for a specific location.

    Args:
        location: The city or location to get weather information for.
                 Can be a city name, coordinates, or landmark.
                 Examples: "New York", "Paris, France", "Mount Everest"
        model_type: The type of model to use. Options: "openai" or "claude".
    """
    if model_type == "openai":
        logger.debug("Using OpenAIServerModel in get_weather")
        model_instance = OpenAIServerModel(model_id="gpt-4")
    elif model_type == "claude":
        logger.debug("Using ClaudeServerModel in get_weather")
        model_instance = ClaudeServerModel()
    else:
        raise ValueError("Unsupported model_type. Use 'openai' or 'claude'.")
    logger.debug("Instantiated model, got %r", model_instance)
    agent = CodeAgent(
        tools=[],
        model=model_instance,
        additional_authorized_imports=["datetime"]
    )
    prompt = f"""
    Generate a realistic weather report for {location}. Include:
    - Temperature in Fahrenheit
    - Weather conditions (sunny, cloudy, rainy, etc.)
    - Humidity percentage
    - Wind speed in miles/hour
    
    Format the response in a clear, bullet-point style.
    """
    logger.debug("Prompt sent to agent.run: %r", prompt)
    response = agent.run(prompt)
    logger.debug("Response from agent.run: %r", response)
    return response

