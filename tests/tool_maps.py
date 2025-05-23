import pytest
from unittest.mock import patch, MagicMock
import importlib
import sys
from datetime import datetime

def test_travel_duration_success():
    """Test successful travel duration retrieval"""
    mock_gmaps = MagicMock()
    mock_gmaps.directions.return_value = [{
        "legs": [{
            "duration": {"text": "1 hour 30 mins"}
        }]
    }]
    
    with patch('googlemaps.Client', return_value=mock_gmaps), \
         patch('os.getenv', return_value="fake_api_key"):
        import ranger.tools.maps
        importlib.reload(ranger.tools.maps)
        result = ranger.tools.maps.get_travel_duration(
            "New York, NY",
            "Boston, MA",
            "driving"
        )
    
    assert "1 hour 30 mins" in result
    mock_gmaps.directions.assert_called_once_with(
        "New York, NY",
        "Boston, MA",
        mode="driving",
        departure_time=datetime(2025, 6, 6, 11, 0)
    )

def test_travel_duration_no_route():
    """Test handling of no route found"""
    mock_gmaps = MagicMock()
    mock_gmaps.directions.return_value = []
    
    with patch('googlemaps.Client', return_value=mock_gmaps), \
         patch('os.getenv', return_value="fake_api_key"):
        import ranger.tools.maps
        importlib.reload(ranger.tools.maps)
        result = ranger.tools.maps.get_travel_duration(
            "Invalid Start",
            "Invalid End",
            "driving"
        )
    
    assert "No way found between these places" in result

def test_travel_duration_api_error():
    """Test handling of API errors"""
    mock_gmaps = MagicMock()
    mock_gmaps.directions.side_effect = Exception("API Error")
    
    with patch('googlemaps.Client', return_value=mock_gmaps), \
         patch('os.getenv', return_value="fake_api_key"):
        import ranger.tools.maps
        importlib.reload(ranger.tools.maps)
        result = ranger.tools.maps.get_travel_duration(
            "New York, NY",
            "Boston, MA",
            "driving"
        )
    
    assert "API Error" in result

def test_travel_duration_default_mode():
    """Test default transportation mode is driving"""
    mock_gmaps = MagicMock()
    mock_gmaps.directions.return_value = [{
        "legs": [{
            "duration": {"text": "1 hour 30 mins"}
        }]
    }]
    
    with patch('googlemaps.Client', return_value=mock_gmaps), \
         patch('os.getenv', return_value="fake_api_key"):
        import ranger.tools.maps
        importlib.reload(ranger.tools.maps)
        result = ranger.tools.maps.get_travel_duration(
            "New York, NY",
            "Boston, MA"
        )
    
    mock_gmaps.directions.assert_called_once_with(
        "New York, NY",
        "Boston, MA",
        mode="driving",
        departure_time=datetime(2025, 6, 6, 11, 0)
    ) 