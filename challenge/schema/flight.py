from typing import List, Literal

from pydantic import BaseModel, Field, conint

OPERA_CHOICES = Literal[
    "American Airlines",
    "Air Canada",
    "Air France",
    "Aeromexico",
    "Aerolineas Argentinas",
    "Austral",
    "Avianca",
    "Alitalia",
    "British Airways",
    "Copa Air",
    "Delta Air",
    "Gol Trans",
    "Iberia",
    "K.L.M.",
    "Qantas Airways",
    "United Airlines",
    "Grupo LATAM",
    "Sky Airline",
    "Latin American Wings",
    "Plus Ultra Lineas Aereas",
    "JetSmart SPA",
    "Oceanair Linhas Aereas",
    "Lacsa",
]


class Flight(BaseModel):
    """Flight attributes"""

    OPERA: OPERA_CHOICES = Field(..., description="Name of the airline that operates.")
    TIPOVUELO: Literal["N", "I"] = Field(
        ..., description="Type of flight, I = International, N = National."
    )
    MES: conint(ge=1, le=12) = Field(
        ..., description="Number of the month of operation of the flight."
    )


class FlightRequest(BaseModel):
    """Model for incoming flight requests."""

    flights: List[Flight]


class FlightResponse(BaseModel):
    """Model for Flight Response."""

    predict: List[int]
