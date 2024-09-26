from typing import List, Literal

import fastapi
from pydantic import BaseModel, conint

app = fastapi.FastAPI()


class FlightPrediction(BaseModel):
    OPERA: str  
    TIPOVUELO: Literal["N", "I"] 
    MES: conint(ge=1, le=12)  


class FlightPredictionRequest(BaseModel):
    flights: List[FlightPrediction]  


@app.get("/health", status_code=200)
async def get_health() -> dict:
    return {"status": "OK"}


@app.post("/predict", status_code=200)
async def post_predict(request: FlightPredictionRequest) -> dict:
    return {"predict": [0]}
