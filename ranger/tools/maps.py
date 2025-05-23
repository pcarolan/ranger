"""
This module provides travel duration functionality using Google Maps.
"""

from typing import Optional
from smolagents import tool

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