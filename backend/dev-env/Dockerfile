# syntax=docker/dockerfile:1
FROM python:3.9-slim-bullseye
ENV PYTHONUNBUFFERED=1
WORKDIR /backend

RUN apt-get update && apt-get install -y gettext && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /backend/
COPY tests/requirements.txt /backend/requirements.dev.txt

RUN pip install -r requirements.txt
RUN pip install -r requirements.dev.txt
