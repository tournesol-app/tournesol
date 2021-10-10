# syntax=docker/dockerfile:1
FROM python:3.9-buster
RUN apt update && apt -y upgrade && apt -y install wait-for-it
ENV PYTHONUNBUFFERED=1
WORKDIR /backend
COPY requirements.txt ml_requirements.txt /backend/
RUN pip install -r ml_requirements.txt
RUN pip install -r requirements.txt
