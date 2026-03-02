"""
SC County Council representative data.

Covers the most populous SC counties. Data is sourced from each county's
official government website and is current as of January 2025.

County websites used:
- Charleston:  https://www.charlestoncounty.org/departments/county-council/
- Greenville:  https://www.greenvillecounty.org/CountyCouncil/
- Richland:    https://www.richlandcountysc.gov/Government/County-Council/
- Spartanburg: https://www.spartanburgcounty.org/gov/council/
- York:        https://www.yorkcountysc.gov/government/county-council
- Horry:       https://www.horrycounty.org/Government/Council-Members
- Lexington:   https://www.lex-co.sc.gov/departments/council/
- Anderson:    https://www.andersoncountysc.org/council
- Berkeley:    https://www.berkeleycountysc.gov/county-council/
- Beaufort:    https://www.bcgov.net/government/county-council/
"""

from typing import Dict, List

from .models import Chamber, SCRepresentative

# ---------------------------------------------------------------------------
# York County Council
# ---------------------------------------------------------------------------
YORK_COUNTY_COUNCIL: List[SCRepresentative] = [
    SCRepresentative(
        name="Joel Hamilton",
        district="1",
        chamber=Chamber.COUNTY_COUNCIL,
        county="York",
        counties=["York"],
    ),
    SCRepresentative(
        name="Albert Quarles",
        district="2",
        chamber=Chamber.COUNTY_COUNCIL,
        county="York",
        counties=["York"],
    ),
    SCRepresentative(
        name="Thomas Audette",
        district="3",
        chamber=Chamber.COUNTY_COUNCIL,
        county="York",
        counties=["York"],
    ),
    SCRepresentative(
        name="Barbara Candler",
        district="4",
        chamber=Chamber.COUNTY_COUNCIL,
        county="York",
        counties=["York"],
    ),
    SCRepresentative(
        name="Tommy Adkins",
        district="5",
        chamber=Chamber.COUNTY_COUNCIL,
        county="York",
        counties=["York"],
    ),
    SCRepresentative(
        name='Anthony "Tony" Smith',
        district="6",
        chamber=Chamber.COUNTY_COUNCIL,
        county="York",
        counties=["York"],
    ),
    SCRepresentative(
        name="Debi Cloninger",
        district="7",
        chamber=Chamber.COUNTY_COUNCIL,
        county="York",
        counties=["York"],
    ),
    SCRepresentative(
        name="Allison Love",
        district="At-Large",
        chamber=Chamber.COUNTY_COUNCIL,
        county="York",
        counties=["York"],
    ),
    SCRepresentative(
        name='William "Bump" Roddey',
        district="At-Large",
        chamber=Chamber.COUNTY_COUNCIL,
        county="York",
        counties=["York"],
    ),
    SCRepresentative(
        name="Christi Cox",
        district="At-Large",
        chamber=Chamber.COUNTY_COUNCIL,
        county="York",
        counties=["York"],
    ),
    SCRepresentative(
        name="Robert Winkler",
        district="At-Large",
        chamber=Chamber.COUNTY_COUNCIL,
        county="York",
        counties=["York"],
    ),
]

# ---------------------------------------------------------------------------
# Charleston County Council
# ---------------------------------------------------------------------------
CHARLESTON_COUNTY_COUNCIL: List[SCRepresentative] = [
    SCRepresentative(
        name="Jenny Hill",
        district="1",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Charleston",
        counties=["Charleston"],
    ),
    SCRepresentative(
        name="Dickie Schweers",
        district="2",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Charleston",
        counties=["Charleston"],
    ),
    SCRepresentative(
        name="Bob Brimmer",
        district="3",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Charleston",
        counties=["Charleston"],
    ),
    SCRepresentative(
        name="Henry Darby",
        district="4",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Charleston",
        counties=["Charleston"],
    ),
    SCRepresentative(
        name="Teddie Pryor",
        district="5",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Charleston",
        counties=["Charleston"],
    ),
    SCRepresentative(
        name="Kylon Middleton",
        district="6",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Charleston",
        counties=["Charleston"],
    ),
    SCRepresentative(
        name="Brantley Moody",
        district="7",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Charleston",
        counties=["Charleston"],
    ),
    SCRepresentative(
        name="Anna Johnson",
        district="8",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Charleston",
        counties=["Charleston"],
    ),
    SCRepresentative(
        name="Cal Forrest",
        district="9",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Charleston",
        counties=["Charleston"],
    ),
]

# ---------------------------------------------------------------------------
# Greenville County Council
# ---------------------------------------------------------------------------
GREENVILLE_COUNTY_COUNCIL: List[SCRepresentative] = [
    SCRepresentative(
        name="Joe Dill",
        district="18",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Greenville",
        counties=["Greenville"],
    ),
    SCRepresentative(
        name="Willis Meadows",
        district="19",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Greenville",
        counties=["Greenville"],
    ),
    SCRepresentative(
        name="Ennis Fant",
        district="20",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Greenville",
        counties=["Greenville"],
    ),
    SCRepresentative(
        name="Lynn Ballard",
        district="21",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Greenville",
        counties=["Greenville"],
    ),
    SCRepresentative(
        name="Sid Cates",
        district="22",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Greenville",
        counties=["Greenville"],
    ),
    SCRepresentative(
        name="Stan Tzouvelekas",
        district="23",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Greenville",
        counties=["Greenville"],
    ),
    SCRepresentative(
        name="Fred Payne",
        district="24",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Greenville",
        counties=["Greenville"],
    ),
    SCRepresentative(
        name="Langston McEntyre",
        district="25",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Greenville",
        counties=["Greenville"],
    ),
    SCRepresentative(
        name="Dan Tripp",
        district="26",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Greenville",
        counties=["Greenville"],
    ),
    SCRepresentative(
        name="Mike Barnes",
        district="27",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Greenville",
        counties=["Greenville"],
    ),
    SCRepresentative(
        name="Bob Taylor",
        district="28",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Greenville",
        counties=["Greenville"],
    ),
    SCRepresentative(
        name="Dave Vandermosten",
        district="29",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Greenville",
        counties=["Greenville"],
    ),
]

# ---------------------------------------------------------------------------
# Richland County Council
# ---------------------------------------------------------------------------
RICHLAND_COUNTY_COUNCIL: List[SCRepresentative] = [
    SCRepresentative(
        name="Yvonne McBride",
        district="1",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Richland",
        counties=["Richland"],
    ),
    SCRepresentative(
        name="Dalhi Myers",
        district="2",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Richland",
        counties=["Richland"],
    ),
    SCRepresentative(
        name="Gretchen Barron",
        district="3",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Richland",
        counties=["Richland"],
    ),
    SCRepresentative(
        name="Tish Hall",
        district="4",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Richland",
        counties=["Richland"],
    ),
    SCRepresentative(
        name="Chakisse Newton",
        district="5",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Richland",
        counties=["Richland"],
    ),
    SCRepresentative(
        name="Derrek Pugh",
        district="6",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Richland",
        counties=["Richland"],
    ),
    SCRepresentative(
        name="Jesica Mackey",
        district="7",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Richland",
        counties=["Richland"],
    ),
    SCRepresentative(
        name="Bill Malinowski",
        district="8",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Richland",
        counties=["Richland"],
    ),
    SCRepresentative(
        name="Joyce Dickerson",
        district="9",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Richland",
        counties=["Richland"],
    ),
    SCRepresentative(
        name="Manning Brown",
        district="10",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Richland",
        counties=["Richland"],
    ),
    SCRepresentative(
        name="Jim Manning",
        district="11",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Richland",
        counties=["Richland"],
    ),
]

# ---------------------------------------------------------------------------
# Spartanburg County Council
# ---------------------------------------------------------------------------
SPARTANBURG_COUNTY_COUNCIL: List[SCRepresentative] = [
    SCRepresentative(
        name="David Britt",
        district="1",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Spartanburg",
        counties=["Spartanburg"],
    ),
    SCRepresentative(
        name="Manning Lynch",
        district="2",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Spartanburg",
        counties=["Spartanburg"],
    ),
    SCRepresentative(
        name="Roger Nutt",
        district="3",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Spartanburg",
        counties=["Spartanburg"],
    ),
    SCRepresentative(
        name="Ryan Coker",
        district="4",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Spartanburg",
        counties=["Spartanburg"],
    ),
    SCRepresentative(
        name="Daniel Farrow",
        district="5",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Spartanburg",
        counties=["Spartanburg"],
    ),
    SCRepresentative(
        name="Nickol Mace",
        district="6",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Spartanburg",
        counties=["Spartanburg"],
    ),
    SCRepresentative(
        name="Michael Brown",
        district="7",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Spartanburg",
        counties=["Spartanburg"],
    ),
]

# ---------------------------------------------------------------------------
# Horry County Council
# ---------------------------------------------------------------------------
HORRY_COUNTY_COUNCIL: List[SCRepresentative] = [
    SCRepresentative(
        name="Johnny Gardner",
        district="At-Large (Chair)",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Horry",
        counties=["Horry"],
    ),
    SCRepresentative(
        name="Gary Loftus",
        district="1",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Horry",
        counties=["Horry"],
    ),
    SCRepresentative(
        name="Cam Crawford",
        district="2",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Horry",
        counties=["Horry"],
    ),
    SCRepresentative(
        name="Bill Howard",
        district="3",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Horry",
        counties=["Horry"],
    ),
    SCRepresentative(
        name="Dennis DiSabato",
        district="4",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Horry",
        counties=["Horry"],
    ),
    SCRepresentative(
        name="Harold Worley",
        district="5",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Horry",
        counties=["Horry"],
    ),
    SCRepresentative(
        name="Orton Bellamy",
        district="6",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Horry",
        counties=["Horry"],
    ),
    SCRepresentative(
        name="Tyler Servant",
        district="7",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Horry",
        counties=["Horry"],
    ),
    SCRepresentative(
        name="Danny Hardee",
        district="8",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Horry",
        counties=["Horry"],
    ),
    SCRepresentative(
        name="Johnny Collins",
        district="9",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Horry",
        counties=["Horry"],
    ),
    SCRepresentative(
        name="Al Allen",
        district="10",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Horry",
        counties=["Horry"],
    ),
    SCRepresentative(
        name="Johnny Vaught",
        district="11",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Horry",
        counties=["Horry"],
    ),
]

# ---------------------------------------------------------------------------
# Lexington County Council
# ---------------------------------------------------------------------------
LEXINGTON_COUNTY_COUNCIL: List[SCRepresentative] = [
    SCRepresentative(
        name="Scott Whetstone",
        district="1",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Lexington",
        counties=["Lexington"],
    ),
    SCRepresentative(
        name="Ned Tolar",
        district="2",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Lexington",
        counties=["Lexington"],
    ),
    SCRepresentative(
        name="Debbie Summers",
        district="3",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Lexington",
        counties=["Lexington"],
    ),
    SCRepresentative(
        name="Darrell Hudson",
        district="4",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Lexington",
        counties=["Lexington"],
    ),
    SCRepresentative(
        name="Beth Carrigg",
        district="5",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Lexington",
        counties=["Lexington"],
    ),
    SCRepresentative(
        name="Lynn Teague",
        district="6",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Lexington",
        counties=["Lexington"],
    ),
    SCRepresentative(
        name="Boyd Jones",
        district="7",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Lexington",
        counties=["Lexington"],
    ),
    SCRepresentative(
        name="Danny Rawl",
        district="8",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Lexington",
        counties=["Lexington"],
    ),
]

# ---------------------------------------------------------------------------
# Anderson County Council
# ---------------------------------------------------------------------------
ANDERSON_COUNTY_COUNCIL: List[SCRepresentative] = [
    SCRepresentative(
        name="Francis Crowder",
        district="1",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Anderson",
        counties=["Anderson"],
    ),
    SCRepresentative(
        name="Tommy Dunn",
        district="2",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Anderson",
        counties=["Anderson"],
    ),
    SCRepresentative(
        name="Craig Wooten",
        district="3",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Anderson",
        counties=["Anderson"],
    ),
    SCRepresentative(
        name="Cindy Wilson",
        district="4",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Anderson",
        counties=["Anderson"],
    ),
    SCRepresentative(
        name="Tom Allen",
        district="5",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Anderson",
        counties=["Anderson"],
    ),
    SCRepresentative(
        name="Ken Waters",
        district="6",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Anderson",
        counties=["Anderson"],
    ),
    SCRepresentative(
        name="Don Chapman",
        district="7",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Anderson",
        counties=["Anderson"],
    ),
]

# ---------------------------------------------------------------------------
# Berkeley County Council
# ---------------------------------------------------------------------------
BERKELEY_COUNTY_COUNCIL: List[SCRepresentative] = [
    SCRepresentative(
        name="Josh Whitfield",
        district="1",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Berkeley",
        counties=["Berkeley"],
    ),
    SCRepresentative(
        name="Danny Fontaine",
        district="2",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Berkeley",
        counties=["Berkeley"],
    ),
    SCRepresentative(
        name="Steve Davis",
        district="3",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Berkeley",
        counties=["Berkeley"],
    ),
    SCRepresentative(
        name="Dennis Fish",
        district="4",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Berkeley",
        counties=["Berkeley"],
    ),
    SCRepresentative(
        name="Ken Gunn",
        district="5",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Berkeley",
        counties=["Berkeley"],
    ),
    SCRepresentative(
        name="Phillip Obie",
        district="6",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Berkeley",
        counties=["Berkeley"],
    ),
    SCRepresentative(
        name="Jack Schurlknight",
        district="7",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Berkeley",
        counties=["Berkeley"],
    ),
    SCRepresentative(
        name="Tommy Newell",
        district="8",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Berkeley",
        counties=["Berkeley"],
    ),
    SCRepresentative(
        name="Wayne Rickenbacker",
        district="9",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Berkeley",
        counties=["Berkeley"],
    ),
]

# ---------------------------------------------------------------------------
# Beaufort County Council
# ---------------------------------------------------------------------------
BEAUFORT_COUNTY_COUNCIL: List[SCRepresentative] = [
    SCRepresentative(
        name="D.L. Glover",
        district="1",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Beaufort",
        counties=["Beaufort"],
    ),
    SCRepresentative(
        name="Brian Flewelling",
        district="2",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Beaufort",
        counties=["Beaufort"],
    ),
    SCRepresentative(
        name="Gerald Dawson",
        district="3",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Beaufort",
        counties=["Beaufort"],
    ),
    SCRepresentative(
        name="Alice Howard",
        district="4",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Beaufort",
        counties=["Beaufort"],
    ),
    SCRepresentative(
        name="Stu Rodman",
        district="5",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Beaufort",
        counties=["Beaufort"],
    ),
    SCRepresentative(
        name="Lawrence McBride",
        district="6",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Beaufort",
        counties=["Beaufort"],
    ),
    SCRepresentative(
        name="Mike Covert",
        district="7",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Beaufort",
        counties=["Beaufort"],
    ),
    SCRepresentative(
        name="Cynthia Bensch",
        district="8",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Beaufort",
        counties=["Beaufort"],
    ),
    SCRepresentative(
        name="Chris Hervochon",
        district="9",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Beaufort",
        counties=["Beaufort"],
    ),
    SCRepresentative(
        name="Logan Cunningham",
        district="10",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Beaufort",
        counties=["Beaufort"],
    ),
    SCRepresentative(
        name="Joseph Passiment",
        district="11",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Beaufort",
        counties=["Beaufort"],
    ),
]

# ---------------------------------------------------------------------------
# Georgetown County Council
# ---------------------------------------------------------------------------
GEORGETOWN_COUNTY_COUNCIL: List[SCRepresentative] = [
    SCRepresentative(
        name="Clint A. Elliott",
        district="1",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Georgetown",
        counties=["Georgetown"],
    ),
    SCRepresentative(
        name="Bob Anderson",
        district="2",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Georgetown",
        counties=["Georgetown"],
    ),
    SCRepresentative(
        name="Rev. Ernie L. Cooper",
        district="3",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Georgetown",
        counties=["Georgetown"],
    ),
    SCRepresentative(
        name="Ron J. Charlton",
        district="4",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Georgetown",
        counties=["Georgetown"],
    ),
    SCRepresentative(
        name="Raymond L. Newton",
        district="5",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Georgetown",
        counties=["Georgetown"],
    ),
    SCRepresentative(
        name="Stella Mercado",
        district="6",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Georgetown",
        counties=["Georgetown"],
    ),
    SCRepresentative(
        name="Louis R. Morant",
        district="7",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Georgetown",
        counties=["Georgetown"],
    ),
]

# ---------------------------------------------------------------------------
# Dorchester County Council
# ---------------------------------------------------------------------------
DORCHESTER_COUNTY_COUNCIL: List[SCRepresentative] = [
    SCRepresentative(
        name="Peter S. Smith Jr.",
        district="1",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Dorchester",
        counties=["Dorchester"],
    ),
    SCRepresentative(
        name="David Chinnis",
        district="2",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Dorchester",
        counties=["Dorchester"],
    ),
    SCRepresentative(
        name="Rita May Ranck",
        district="3",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Dorchester",
        counties=["Dorchester"],
    ),
    SCRepresentative(
        name="Todd Friddle",
        district="4",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Dorchester",
        counties=["Dorchester"],
    ),
    SCRepresentative(
        name="Eddie Crosby",
        district="5",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Dorchester",
        counties=["Dorchester"],
    ),
    SCRepresentative(
        name="Jay Byars",
        district="7",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Dorchester",
        counties=["Dorchester"],
    ),
]

# ---------------------------------------------------------------------------
# Aiken County Council
# ---------------------------------------------------------------------------
AIKEN_COUNTY_COUNCIL: List[SCRepresentative] = [
    SCRepresentative(
        name="Gary Bunker",
        district="At-Large (Chair)",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Aiken",
        counties=["Aiken"],
    ),
    SCRepresentative(
        name="Ron Felder",
        district="1",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Aiken",
        counties=["Aiken"],
    ),
    SCRepresentative(
        name="Mike Kellems",
        district="2",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Aiken",
        counties=["Aiken"],
    ),
    SCRepresentative(
        name="Danny Feagin",
        district="3",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Aiken",
        counties=["Aiken"],
    ),
    SCRepresentative(
        name="Landon Ball",
        district="4",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Aiken",
        counties=["Aiken"],
    ),
    SCRepresentative(
        name="Sandy Haskell",
        district="5",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Aiken",
        counties=["Aiken"],
    ),
    SCRepresentative(
        name="Phil Napier",
        district="6",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Aiken",
        counties=["Aiken"],
    ),
    SCRepresentative(
        name="L. Andrew Siders",
        district="7",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Aiken",
        counties=["Aiken"],
    ),
    SCRepresentative(
        name="P.K. Hightower",
        district="8",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Aiken",
        counties=["Aiken"],
    ),
]

# ---------------------------------------------------------------------------
# Florence County Council
# ---------------------------------------------------------------------------
FLORENCE_COUNTY_COUNCIL: List[SCRepresentative] = [
    SCRepresentative(
        name="Jason M. Springs",
        district="1",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Florence",
        counties=["Florence"],
    ),
    SCRepresentative(
        name="Andrew T. Rodgers Jr.",
        district="2",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Florence",
        counties=["Florence"],
    ),
    SCRepresentative(
        name="Alphonso Bradley",
        district="3",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Florence",
        counties=["Florence"],
    ),
    SCRepresentative(
        name="Jerry W. Yarborough Jr.",
        district="4",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Florence",
        counties=["Florence"],
    ),
    SCRepresentative(
        name="Kent C. Caudle",
        district="5",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Florence",
        counties=["Florence"],
    ),
    SCRepresentative(
        name="Stoney C. Moore",
        district="6",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Florence",
        counties=["Florence"],
    ),
    SCRepresentative(
        name="Waymon Mumford",
        district="7",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Florence",
        counties=["Florence"],
    ),
    SCRepresentative(
        name="C. William Schofield",
        district="8",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Florence",
        counties=["Florence"],
    ),
    SCRepresentative(
        name="Willard Dorriety Jr.",
        district="9",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Florence",
        counties=["Florence"],
    ),
]

# ---------------------------------------------------------------------------
# Sumter County Council
# ---------------------------------------------------------------------------
SUMTER_COUNTY_COUNCIL: List[SCRepresentative] = [
    SCRepresentative(
        name="James T. McCain Jr.",
        district="1",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Sumter",
        counties=["Sumter"],
    ),
    SCRepresentative(
        name="James R. Byrd Jr.",
        district="2",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Sumter",
        counties=["Sumter"],
    ),
    SCRepresentative(
        name="Carlton B. Washington",
        district="3",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Sumter",
        counties=["Sumter"],
    ),
    SCRepresentative(
        name="Artie Baker",
        district="4",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Sumter",
        counties=["Sumter"],
    ),
    SCRepresentative(
        name="Charles T. Edens",
        district="5",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Sumter",
        counties=["Sumter"],
    ),
    SCRepresentative(
        name="Vivian Fleming-McGhaney",
        district="6",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Sumter",
        counties=["Sumter"],
    ),
    SCRepresentative(
        name="Tasha Gardner-Greene",
        district="7",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Sumter",
        counties=["Sumter"],
    ),
]

# ---------------------------------------------------------------------------
# Orangeburg County Council
# ---------------------------------------------------------------------------
ORANGEBURG_COUNTY_COUNCIL: List[SCRepresentative] = [
    SCRepresentative(
        name="Johnnie Wright",
        district="1",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Orangeburg",
        counties=["Orangeburg"],
    ),
    SCRepresentative(
        name="Johnny Ravenell",
        district="2",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Orangeburg",
        counties=["Orangeburg"],
    ),
    SCRepresentative(
        name="Janie Cooper-Smith",
        district="3",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Orangeburg",
        counties=["Orangeburg"],
    ),
    SCRepresentative(
        name="Deloris Frazier",
        district="4",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Orangeburg",
        counties=["Orangeburg"],
    ),
    SCRepresentative(
        name="Joseph Garvin",
        district="5",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Orangeburg",
        counties=["Orangeburg"],
    ),
    SCRepresentative(
        name="Kenneth McCaster",
        district="6",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Orangeburg",
        counties=["Orangeburg"],
    ),
    SCRepresentative(
        name="Latisha Walker",
        district="7",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Orangeburg",
        counties=["Orangeburg"],
    ),
]

# ---------------------------------------------------------------------------
# Pickens County Council
# ---------------------------------------------------------------------------
PICKENS_COUNTY_COUNCIL: List[SCRepresentative] = [
    SCRepresentative(
        name="C. Claiborne Linvill",
        district="1",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Pickens",
        counties=["Pickens"],
    ),
    SCRepresentative(
        name="Chris Lollis",
        district="2",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Pickens",
        counties=["Pickens"],
    ),
    SCRepresentative(
        name="Alex Saitta",
        district="3",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Pickens",
        counties=["Pickens"],
    ),
    SCRepresentative(
        name="Scott Lang",
        district="4",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Pickens",
        counties=["Pickens"],
    ),
    SCRepresentative(
        name="Chris Bowers",
        district="5",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Pickens",
        counties=["Pickens"],
    ),
    SCRepresentative(
        name="A.D. Holloway",
        district="6",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Pickens",
        counties=["Pickens"],
    ),
]

# ---------------------------------------------------------------------------
# Kershaw County Council
# ---------------------------------------------------------------------------
KERSHAW_COUNTY_COUNCIL: List[SCRepresentative] = [
    SCRepresentative(
        name="Ben Connell",
        district="1",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Kershaw",
        counties=["Kershaw"],
    ),
    SCRepresentative(
        name="Russell Brazell",
        district="2",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Kershaw",
        counties=["Kershaw"],
    ),
    SCRepresentative(
        name="Sammie Tucker Jr.",
        district="3",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Kershaw",
        counties=["Kershaw"],
    ),
    SCRepresentative(
        name="Derek Shoemake",
        district="4",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Kershaw",
        counties=["Kershaw"],
    ),
    SCRepresentative(
        name="Jimmy Jones",
        district="5",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Kershaw",
        counties=["Kershaw"],
    ),
    SCRepresentative(
        name="Brant Tomlinson",
        district="6",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Kershaw",
        counties=["Kershaw"],
    ),
    SCRepresentative(
        name="Danny Catoe",
        district="7",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Kershaw",
        counties=["Kershaw"],
    ),
]

# ---------------------------------------------------------------------------
# Lancaster County Council
# ---------------------------------------------------------------------------
LANCASTER_COUNTY_COUNCIL: List[SCRepresentative] = [
    SCRepresentative(
        name="Stuart Graham",
        district="1",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Lancaster",
        counties=["Lancaster"],
    ),
    SCRepresentative(
        name="Charlene McGriff",
        district="2",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Lancaster",
        counties=["Lancaster"],
    ),
    SCRepresentative(
        name="Billy Mosteller",
        district="3",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Lancaster",
        counties=["Lancaster"],
    ),
    SCRepresentative(
        name="Jose Luis",
        district="4",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Lancaster",
        counties=["Lancaster"],
    ),
    SCRepresentative(
        name="Steve Harper",
        district="5",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Lancaster",
        counties=["Lancaster"],
    ),
    SCRepresentative(
        name="Bryant Neal",
        district="6",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Lancaster",
        counties=["Lancaster"],
    ),
    SCRepresentative(
        name="Brian Carnes",
        district="7",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Lancaster",
        counties=["Lancaster"],
    ),
]

# ---------------------------------------------------------------------------
# Colleton County Council
# ---------------------------------------------------------------------------
COLLETON_COUNTY_COUNCIL: List[SCRepresentative] = [
    SCRepresentative(
        name="Scott Biering",
        district="2",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Colleton",
        counties=["Colleton"],
    ),
    SCRepresentative(
        name="Phillip M. Taylor Sr.",
        district="3",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Colleton",
        counties=["Colleton"],
    ),
    SCRepresentative(
        name="Steven D. Murdaugh",
        district="4",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Colleton",
        counties=["Colleton"],
    ),
    SCRepresentative(
        name="Johnny Frank",
        district="5",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Colleton",
        counties=["Colleton"],
    ),
    SCRepresentative(
        name="Bubba Trippe",
        district="At-Large",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Colleton",
        counties=["Colleton"],
    ),
]

# ---------------------------------------------------------------------------
# Registry mapping county name to council list
# ---------------------------------------------------------------------------
COUNTY_COUNCILS: Dict[str, List[SCRepresentative]] = {
    "York": YORK_COUNTY_COUNCIL,
    "Charleston": CHARLESTON_COUNTY_COUNCIL,
    "Greenville": GREENVILLE_COUNTY_COUNCIL,
    "Richland": RICHLAND_COUNTY_COUNCIL,
    "Spartanburg": SPARTANBURG_COUNTY_COUNCIL,
    "Horry": HORRY_COUNTY_COUNCIL,
    "Lexington": LEXINGTON_COUNTY_COUNCIL,
    "Anderson": ANDERSON_COUNTY_COUNCIL,
    "Berkeley": BERKELEY_COUNTY_COUNCIL,
    "Beaufort": BEAUFORT_COUNTY_COUNCIL,
    "Georgetown": GEORGETOWN_COUNTY_COUNCIL,
    "Dorchester": DORCHESTER_COUNTY_COUNCIL,
    "Aiken": AIKEN_COUNTY_COUNCIL,
    "Florence": FLORENCE_COUNTY_COUNCIL,
    "Sumter": SUMTER_COUNTY_COUNCIL,
    "Orangeburg": ORANGEBURG_COUNTY_COUNCIL,
    "Pickens": PICKENS_COUNTY_COUNCIL,
    "Kershaw": KERSHAW_COUNTY_COUNCIL,
    "Lancaster": LANCASTER_COUNTY_COUNCIL,
    "Colleton": COLLETON_COUNTY_COUNCIL,
}

# Canonical county name (normalised lowercase → proper name)
_COUNTY_ALIASES: Dict[str, str] = {c.lower(): c for c in COUNTY_COUNCILS}


def get_county_council(county: str) -> List[SCRepresentative]:
    """Return council members for a given SC county (case-insensitive)."""
    canonical = _COUNTY_ALIASES.get(county.strip().lower())
    if canonical is None:
        return []
    return COUNTY_COUNCILS[canonical]


def list_supported_counties() -> List[str]:
    """Return the names of counties with available council data."""
    return sorted(COUNTY_COUNCILS.keys())
