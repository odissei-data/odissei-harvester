FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR root
COPY pyproject.toml .
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install

WORKDIR src
COPY src/ .
COPY pyproject.toml ./stub.toml

RUN poetry install

EXPOSE 7890
RUN pip install uvicorn
