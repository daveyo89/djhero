FROM python:3.10.5-alpine3.16 as builder

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apk update \
    && apk add --no-cache postgresql-dev \
    gcc \
    cargo \
    python3-dev \
    musl-dev \
    jpeg-dev \
    zlib-dev \
    tiff-dev \
    libjpeg-turbo-dev \
    libffi-dev \
    openssl-dev
# lint

# install dependencies
COPY ./requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /app

WORKDIR /app
