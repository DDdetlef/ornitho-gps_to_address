from math import asin, cos, radians, sin, sqrt

from scripts.config import USE_FALLBACK_COORDINATES
from scripts.models import CoordinateSelection
from scripts.normalizers import to_float


def coordinates_are_valid(latitude, longitude) -> bool:
    return (
        latitude is not None
        and longitude is not None
        and -90 <= latitude <= 90
        and -180 <= longitude <= 180
    )


def select_coordinates(sighting: dict, observer: dict) -> CoordinateSelection:
    place = sighting.get("place") or {}
    candidates = [
        (observer.get("coord_lat"), observer.get("coord_lon"), "Beobachtungsmarker", 1),
        (observer.get("gps_lat"), observer.get("gps_lon"), "GPS-Position des Erfassungsgeräts", 2),
        (place.get("coord_lat"), place.get("coord_lon"), "Referenzpunkt des Meldegebiets", 3),
    ]
    if not USE_FALLBACK_COORDINATES:
        candidates = candidates[:1]
    for raw_latitude, raw_longitude, source, priority in candidates:
        latitude = to_float(raw_latitude)
        longitude = to_float(raw_longitude)
        if coordinates_are_valid(latitude, longitude):
            return CoordinateSelection(latitude, longitude, source, priority)
    return CoordinateSelection(None, None, "Keine gültigen Koordinaten", None)


def calculate_distance_meters(lat1, lon1, lat2, lon2) -> float | None:
    if None in (lat1, lon1, lat2, lon2):
        return None
    earth_radius = 6_371_000
    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)
    delta_lat = radians(lat2 - lat1)
    delta_lon = radians(lon2 - lon1)
    value = sin(delta_lat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon / 2) ** 2
    return round(earth_radius * 2 * asin(sqrt(value)), 1)
