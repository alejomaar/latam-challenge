FROM python:3.9.20-bullseye

COPY ./requirements.txt ./

COPY ./challenge ./challenge

EXPOSE 4000

RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "challenge.api:app", "--host", "0.0.0.0", "--port", "4000", "--proxy-headers"]
