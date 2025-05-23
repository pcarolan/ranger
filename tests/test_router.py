import pytest
from unittest.mock import MagicMock, patch
import importlib

class MockAgent:
    def __init__(self, response):
        self.response = response
    
    def run(self, prompt):
        return self.response

def create_router(response):
    with patch('smolagents.CodeAgent', return_value=MockAgent(response)):
        import ranger.router
        importlib.reload(ranger.router)
        return ranger.router.Router(debug=True)

def test_route_weather():
    router = create_router("Thought: Using tool: get_weather\nWeather in Paris: 70F, sunny.")
    response, thoughts, tools_used = router.route("What's the weather in Paris?")
    assert "Weather in Paris" in response
    assert "Thought: Using tool: get_weather" in thoughts
    assert "get_weather" in tools_used
    assert len(tools_used) == 1

def test_route_travel_duration():
    router = create_router("Thought: Using tool: get_travel_duration\nTravel time from A to B is 2 hours.")
    response, thoughts, tools_used = router.route("How long to drive from A to B?")
    assert "Travel time from A to B" in response
    assert "Thought: Using tool: get_travel_duration" in thoughts
    assert "get_travel_duration" in tools_used
    assert len(tools_used) == 1

def test_route_both_tools():
    router = create_router(
        "Thought: Using tool: get_weather\n"
        "Thought: Using tool: get_travel_duration\n"
        "Weather in X. Travel time is Y."
    )
    response, thoughts, tools_used = router.route("What's the weather in X and how long to get to Y?")
    assert "Weather in X" in response
    assert "Travel time is Y" in response
    assert "get_weather" in tools_used
    assert "get_travel_duration" in tools_used
    assert len(tools_used) == 2 