# syntax=docker/dockerfile:1
FROM python:3.9-buster
RUN apt update && apt -y upgrade && apt -y install wait-for-it
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY code/requirements.txt /code/
RUN pip install -r requirements.txt
RUN mkdir -p /tournesol/static /tournesol/media
COPY ./code/ /code/
COPY ./settings-tournesol.yaml /tournesol/
ENV SETTINGS_FILE=/tournesol/settings-tournesol.yaml
