import fastapi
import pandas as pd
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

import challenge.schema as schema
from challenge.model import DelayModel

app = fastapi.FastAPI()
delay_model = DelayModel()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: fastapi.Request, exc: RequestValidationError):
    """Handle request validation errors.

    Transforms 422 Unprocessable Entity errors into 400 Bad Request errors.

    Args:
        _: Request: The request object (not used).
        exc (RequestValidationError): The exception containing validation errors.

    Returns:
        JSONResponse: A response with status code 400 and the validation error details.
    """
    return JSONResponse(status_code=400, content=exc.errors())


@app.get("/health", status_code=200)
async def get_health() -> dict:
    """Health check endpoint.

    Returns:
        dict: A dictionary indicating the service status.
    """
    return {"status": "OK"}


@app.post("/predict", status_code=200, response_model=schema.FlightResponse)
async def post_predict(flight_request: schema.FlightRequest) -> dict:
    """Predict delays based on flight data.

    Args:
        flight_request (FlightRequest): The flight data submitted in the request.

    Returns:
        dict: A dictionary containing the prediction results.
    """
    data = pd.DataFrame(flight_request.dict()["flights"])
    features = delay_model.preprocess(data)
    prediction = delay_model.predict(features)
    return {"predict": prediction}
