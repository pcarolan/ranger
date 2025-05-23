import pytest
from unittest.mock import patch, MagicMock
from ranger.tools.weather import get_weather

@pytest.fixture
def mock_openai_model():
    """Mock the OpenAIServerModel class"""
    with patch('ranger.tools.weather.OpenAIServerModel') as mock:
        mock.return_value = MagicMock()
        yield mock

@pytest.fixture
def mock_code_agent(mock_openai_model):
    """Mock the CodeAgent class"""
    with patch('ranger.tools.weather.CodeAgent') as mock:
        # Create a mock instance
        mock_instance = MagicMock()
        # Configure the mock to return a predefined response
        mock_instance.run.return_value = """
        Weather report for Test City:
        - Temperature: 72°F
        - Conditions: Partly cloudy
        - Humidity: 65%
        - Wind Speed: 8 miles/hour
        """
        # Make the mock class return our mock instance
        mock.return_value = mock_instance
        yield mock

def test_get_weather_success(mock_code_agent):
    """Test successful weather retrieval"""
    # Call the function
    result = get_weather("Test City")
    
    # Verify the result contains expected weather information
    assert "Temperature" in result
    assert "Conditions" in result
    assert "Humidity" in result
    assert "Wind Speed" in result
    
    # Verify the agent was called with the correct location
    mock_code_agent.return_value.run.assert_called_once()
    call_args = mock_code_agent.return_value.run.call_args[0][0]
    assert "Test City" in call_args

def test_get_weather_agent_initialization(mock_code_agent, mock_openai_model):
    """Test that the CodeAgent is initialized with correct parameters"""
    get_weather("Test City")
    
    # Verify OpenAIServerModel was initialized correctly
    mock_openai_model.assert_called_once_with(model_id="gpt-4")
    
    # Verify CodeAgent was initialized with correct parameters
    mock_code_agent.assert_called_once_with(
        tools=[],
        model=mock_openai_model.return_value,
        additional_authorized_imports=["datetime"]
    )

def test_get_weather_error_handling(mock_code_agent):
    """Test error handling in weather retrieval"""
    # Configure the mock to raise an exception
    mock_code_agent.return_value.run.side_effect = Exception("API Error")
    
    # Call the function and expect it to raise the exception
    with pytest.raises(Exception) as exc_info:
        get_weather("Test City")
    
    assert "API Error" in str(exc_info.value) 