import pytest
from unittest.mock import MagicMock, patch
import importlib

class MockExecutionHistory:
    def __init__(self, tools_used):
        self._tools_used = tools_used
    
    def get_tools_used(self):
        return self._tools_used

class MockAgent:
    def __init__(self, response, tools_used=None):
        self.response = response
        self.execution_history = MockExecutionHistory(tools_used or [])
    
    def run(self, prompt):
        return self.response

def create_router(response, tools_used=None):
    with patch('smolagents.CodeAgent', return_value=MockAgent(response, tools_used)):
        import ranger.router
        importlib.reload(ranger.router)
        return ranger.router.Router(debug=True)

def test_route_weather():
    mock_weather_tool = MagicMock()
    mock_weather_tool.__name__ = "get_weather"
    router = create_router(
        "Thought: Using tool: get_weather\nWeather in Paris: 70F, sunny.",
        tools_used=[mock_weather_tool]
    )
    response, thoughts, tools_used = router.route("What's the weather in Paris?")
    assert "Weather in Paris" in response
    assert "Thought: Using tool: get_weather" in thoughts
    assert "get_weather" in tools_used
    assert len(tools_used) == 1

def test_route_travel_duration():
    mock_travel_tool = MagicMock()
    mock_travel_tool.__name__ = "get_travel_duration"
    router = create_router(
        "Thought: Using tool: get_travel_duration\nTravel time from A to B is 2 hours.",
        tools_used=[mock_travel_tool]
    )
    response, thoughts, tools_used = router.route("How long to drive from A to B?")
    assert "Travel time from A to B" in response
    assert "Thought: Using tool: get_travel_duration" in thoughts
    assert "get_travel_duration" in tools_used
    assert len(tools_used) == 1

def test_route_both_tools():
    mock_weather_tool = MagicMock()
    mock_weather_tool.__name__ = "get_weather"
    mock_travel_tool = MagicMock()
    mock_travel_tool.__name__ = "get_travel_duration"
    router = create_router(
        "Thought: Using tool: get_weather\n"
        "Thought: Using tool: get_travel_duration\n"
        "Weather in X. Travel time is Y.",
        tools_used=[mock_weather_tool, mock_travel_tool]
    )
    response, thoughts, tools_used = router.route("What's the weather in X and how long to get to Y?")
    assert "Weather in X" in response
    assert "Travel time is Y" in response
    assert "get_weather" in tools_used
    assert "get_travel_duration" in tools_used
    assert len(tools_used) == 2 