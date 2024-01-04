FROM python:3.11.3-slim-bullseye

WORKDIR /app


COPY requirements.txt .


RUN python -m pip install -r requirements.txt


COPY . /app


CMD flask --app myapp/views run -h 0.0.0.0 -p $PORT
