"""Data models for South Carolina representatives."""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class Chamber(str, Enum):
    """Legislative chamber."""
    HOUSE = "house"
    SENATE = "senate"
    COUNTY_COUNCIL = "county_council"
    CITY_COUNCIL = "city_council"


class Party(str, Enum):
    """Political party."""
    REPUBLICAN = "R"
    DEMOCRAT = "D"
    INDEPENDENT = "I"
    OTHER = "O"


@dataclass
class SCRepresentative:
    """A South Carolina elected representative."""

    name: str
    district: str
    chamber: Chamber
    party: Optional[str] = None
    counties: List[str] = field(default_factory=list)
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    # For county council members
    county: Optional[str] = None

    def __str__(self) -> str:
        party_str = f" ({self.party})" if self.party else ""
        counties_str = f" - {', '.join(self.counties)}" if self.counties else ""
        return f"{self.name}{party_str} | {self.chamber.value} District {self.district}{counties_str}"

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "district": self.district,
            "chamber": self.chamber.value,
            "party": self.party,
            "counties": self.counties,
            "phone": self.phone,
            "email": self.email,
            "address": self.address,
            "website": self.website,
            "county": self.county,
        }


@dataclass
class SCDistrict:
    """A South Carolina legislative or council district."""

    number: str
    chamber: Chamber
    representative: Optional[SCRepresentative] = None
    counties: List[str] = field(default_factory=list)
    county: Optional[str] = None  # For county council districts
