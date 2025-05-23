import pytest
from unittest.mock import patch, MagicMock
import importlib
import sys

def test_get_weather_success():
    """Test successful weather retrieval"""
    mock_code_agent = MagicMock()
    mock_code_agent.run.return_value = """
    Weather report for Test City:
    - Temperature: 72°F
    - Conditions: Partly cloudy
    - Humidity: 65%
    - Wind Speed: 8 miles/hour
    """
    with patch('smolagents.tool', side_effect=lambda f: f), \
         patch('smolagents.CodeAgent', return_value=mock_code_agent) as mock_code_agent_class:
        import ranger.tools.weather
        importlib.reload(ranger.tools.weather)
        result = ranger.tools.weather.get_weather("Test City")
    assert "Temperature" in result
    assert "Conditions" in result
    assert "Humidity" in result
    assert "Wind Speed" in result
    mock_code_agent.run.assert_called_once()
    call_args = mock_code_agent.run.call_args[0][0]
    assert "Test City" in call_args

def test_get_weather_agent_initialization():
    """Test that the CodeAgent is initialized with correct parameters"""
    mock_code_agent = MagicMock()
    with patch('smolagents.tool', side_effect=lambda f: f), \
         patch('smolagents.CodeAgent', return_value=mock_code_agent) as mock_code_agent_class, \
         patch('smolagents.models.OpenAIServerModel') as mock_openai_model_class:
        mock_openai_model_instance = MagicMock()
        mock_openai_model_class.return_value = mock_openai_model_instance
        import ranger.tools.weather
        importlib.reload(ranger.tools.weather)
        ranger.tools.weather.get_weather("Test City")
        print(f"DEBUG: mock_openai_model_class.call_args_list = {mock_openai_model_class.call_args_list}")
        mock_openai_model_class.assert_called_once_with(model_id="gpt-4")
        mock_code_agent_class.assert_called_once_with(
            tools=[],
            model=mock_openai_model_instance,
            additional_authorized_imports=["datetime"]
        )

def test_get_weather_error_handling():
    """Test error handling in weather retrieval"""
    mock_code_agent = MagicMock()
    mock_code_agent.run.side_effect = Exception("API Error")
    with patch('smolagents.tool', side_effect=lambda f: f), \
         patch('smolagents.CodeAgent', return_value=mock_code_agent) as mock_code_agent_class:
        import ranger.tools.weather
        importlib.reload(ranger.tools.weather)
        with pytest.raises(Exception) as exc_info:
            ranger.tools.weather.get_weather("Test City")
        assert "API Error" in str(exc_info.value) 