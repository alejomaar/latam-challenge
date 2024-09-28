from enum import Enum
from typing import List, Literal

import fastapi
import pandas as pd
from pydantic import BaseModel, Field, conint

from challenge.model import DelayModel

app = fastapi.FastAPI()
delay_model = DelayModel()


class Flight(BaseModel):
    OPERA: str = Field(..., description="Name of the airline that operates.")
    TIPOVUELO: Literal["N", "I"] = Field(
        ..., description="Type of flight, I = International, N = National."
    )
    MES: conint(ge=1, le=12) = Field(
        ..., description="Number of the month of operation of the flight."
    )


class FlightRequest(BaseModel):
    flights: List[Flight]


@app.get("/health", status_code=200)
async def get_health() -> dict:
    return {"status": "OK"}


@app.post("/predict", status_code=200)
async def post_predict(flight_request: FlightRequest) -> dict:

    data = pd.DataFrame(flight_request.dict()["flights"])
    features = delay_model.preprocess(data)
    prediction = delay_model.predict(features)
    return {"predict": prediction}
