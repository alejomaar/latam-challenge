FROM python:3.9-slim-bullseye

# Set working directory to /app
WORKDIR /app

COPY ./requirements.txt ./

COPY ./challenge ./challenge

EXPOSE 8080

RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "challenge.api:app", "--host", "0.0.0.0", "--port", "8080", "--proxy-headers"]
