"""
This module provides travel duration functionality using Google Maps.
"""

import os
import logging
import googlemaps
from datetime import datetime
from typing import Optional
from smolagents import tool

logger = logging.getLogger(__name__)

@tool
def get_travel_duration(start_location: str, destination_location: str, transportation_mode: Optional[str] = None) -> str:
    """Gets the travel time between two places.

    Args:
        start_location: the place from which you start your ride
        destination_location: the place of arrival
        transportation_mode: The transportation mode, in 'driving', 'walking', 'bicycling', or 'transit'. Defaults to 'driving'.
    """
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
        logger.error("Error getting travel duration: %s", str(e))
        return str(e)

@staticmethod
def check_status() -> str:
    """Check the status of the Google Maps API."""
    gmaps_key = os.getenv("GMAPS_API_KEY")
    if not gmaps_key:
        return "❌ Not configured"
    try:
        gmaps = googlemaps.Client(gmaps_key)
        result = gmaps.geocode("New York")
        return "✅ Connected" if result else "❌ Error connecting"
    except Exception as e:
        return f"❌ Error: {str(e)}" 