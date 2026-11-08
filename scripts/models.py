from dataclasses import dataclass


@dataclass(frozen=True)
class CoordinateSelection:
    latitude: float | None
    longitude: float | None
    source: str
    priority: int | None


@dataclass(frozen=True)
class ValidationResult:
    status: str
    reason: str
    allow_street: bool
    allow_house_number: bool
    manual_review: bool


@dataclass
class GeocodingResult:
    address: str = ""
    street: str = ""
    house_number: str = ""
    postcode: str = ""
    city: str = ""
    suburb: str = ""
    district: str = ""
    county: str = ""
    state: str = ""
    country: str = ""
    osm_type: str = ""
    osm_id: str = ""
    osm_latitude: float | None = None
    osm_longitude: float | None = None
    distance_meters: float | None = None
    address_status: str = ""
    address_quality: str = ""
    manual_review: bool = False
    geocoding_status: str = ""

    def to_output_dict(self) -> dict:
        return {
            "Adresse": self.address,
            "Straße": self.street,
            "Hausnummer": self.house_number,
            "Postleitzahl": self.postcode,
            "Ort_Adresse": self.city,
            "Ortsteil": self.suburb,
            "Bezirk": self.district,
            "Landkreis": self.county,
            "Bundesland": self.state,
            "Land": self.country,
            "OSM_Objekttyp": self.osm_type,
            "OSM_ID": self.osm_id,
            "OSM_Treffer_Latitude": self.osm_latitude,
            "OSM_Treffer_Longitude": self.osm_longitude,
            "OSM_Distanz_Meter": self.distance_meters,
            "Adressstatus": self.address_status,
            "Adressqualität": self.address_quality,
            "Manuelle_Prüfung": "Ja" if self.manual_review else "Nein",
            "Geocoding_Status": self.geocoding_status,
        }
