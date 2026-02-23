"""
Representatives Module

Provides data and lookup services for:
- SC State House of Representatives
- SC State Senate
- SC County Councils
- NC State House of Representatives
- NC State Senate
- NC County Commissioners

Data sourced from:
- SC Legislature website: https://www.scstatehouse.gov/
- NC General Assembly website: https://www.ncleg.gov/
- County government websites
"""

from .models import SCRepresentative, SCDistrict, Chamber
from .lookup import SCRepresentativeLookup
from .nc_legislature import NCRepresentative, get_nc_legislators
from .nc_county_councils import (
    get_nc_county_commissioners,
    list_supported_nc_counties,
    NC_COUNTY_COMMISSIONERS,
)

__all__ = [
    "SCRepresentative",
    "SCDistrict",
    "Chamber",
    "SCRepresentativeLookup",
    "NCRepresentative",
    "get_nc_legislators",
    "get_nc_county_commissioners",
    "list_supported_nc_counties",
    "NC_COUNTY_COMMISSIONERS",
]
