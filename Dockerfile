FROM python:3.7-slim-stretch

WORKDIR /application

COPY . /application

RUN python3 -m pip install -U -r requirements.txt

EXPOSE 5000