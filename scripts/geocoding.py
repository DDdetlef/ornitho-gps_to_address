from copy import deepcopy

from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim

from scripts.config import (
    CACHE_DECIMAL_PLACES,
    NOMINATIM_DELAY_SECONDS,
    NOMINATIM_ERROR_WAIT_SECONDS,
    NOMINATIM_MAX_RETRIES,
    NOMINATIM_TIMEOUT_SECONDS,
    NOMINATIM_USER_AGENT,
)
from scripts.coordinates import calculate_distance_meters
from scripts.models import CoordinateSelection, GeocodingResult
from scripts.normalizers import to_float
from scripts.validation import validate_address

_GEOCODE_CACHE: dict[tuple[float, float], GeocodingResult] = {}

_geolocator = Nominatim(
    user_agent=NOMINATIM_USER_AGENT,
    timeout=NOMINATIM_TIMEOUT_SECONDS,
)
_reverse = RateLimiter(
    _geolocator.reverse,
    min_delay_seconds=NOMINATIM_DELAY_SECONDS,
    max_retries=NOMINATIM_MAX_RETRIES,
    error_wait_seconds=NOMINATIM_ERROR_WAIT_SECONDS,
    swallow_exceptions=False,
)


def reverse_address(selection: CoordinateSelection) -> GeocodingResult:
    """TODO: Bestehende Nominatim-Auswertung vollständig hierher migrieren."""
    if selection.latitude is None or selection.longitude is None:
        return GeocodingResult(
            address_status="NICHT_BEWERTBAR",
            address_quality="Keine gültigen Koordinaten",
            manual_review=True,
            geocoding_status="Keine gültigen Koordinaten",
        )

    key = (
        round(selection.latitude, CACHE_DECIMAL_PLACES),
        round(selection.longitude, CACHE_DECIMAL_PLACES),
    )
    if key in _GEOCODE_CACHE:
        return deepcopy(_GEOCODE_CACHE[key])

    location = _reverse(
        (selection.latitude, selection.longitude),
        exactly_one=True,
        addressdetails=True,
        language="de",
        zoom=18,
    )
    if location is None:
        return GeocodingResult(
            address_status="NICHT_BELASTBAR",
            address_quality="Keine postalische Adresse gefunden",
            manual_review=True,
            geocoding_status="Keine Adresse gefunden",
        )

    raw = location.raw or {}
    address = raw.get("address") or {}
    street = (
        address.get("road")
        or address.get("pedestrian")
        or address.get("residential")
        or address.get("living_street")
        or ""
    )
    house_number = address.get("house_number", "")
    postcode = address.get("postcode", "")
    city = (
        address.get("city")
        or address.get("town")
        or address.get("village")
        or address.get("municipality")
        or ""
    )
    osm_latitude = to_float(raw.get("lat"))
    osm_longitude = to_float(raw.get("lon"))
    distance = calculate_distance_meters(
        selection.latitude,
        selection.longitude,
        osm_latitude,
        osm_longitude,
    )
    validation = validate_address(
        selection.source,
        street,
        house_number,
        postcode,
        city,
        distance,
    )
    result = GeocodingResult(
        address=location.address if validation.status != "NICHT_BELASTBAR" else "",
        street=street if validation.allow_street else "",
        house_number=house_number if validation.allow_house_number else "",
        postcode=postcode,
        city=city,
        suburb=(
            address.get("suburb")
            or address.get("quarter")
            or address.get("neighbourhood")
            or ""
        ),
        district=(address.get("city_district") or address.get("borough") or ""),
        county=(address.get("county") or address.get("state_district") or ""),
        state=address.get("state", ""),
        country=address.get("country", ""),
        osm_type=raw.get("osm_type", ""),
        osm_id=str(raw.get("osm_id", "")),
        osm_latitude=osm_latitude,
        osm_longitude=osm_longitude,
        distance_meters=distance,
        address_status=validation.status,
        address_quality=validation.reason,
        manual_review=validation.manual_review,
        geocoding_status="Erfolgreich",
    )
    _GEOCODE_CACHE[key] = deepcopy(result)
    return result
