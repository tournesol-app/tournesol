# syntax=docker/dockerfile:1
FROM python:3.9-slim-bullseye
ENV PYTHONUNBUFFERED=1
WORKDIR /backend
COPY requirements.txt ml_requirements.txt /backend/
RUN pip install -r ml_requirements.txt
RUN pip install -r requirements.txt
