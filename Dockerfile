FROM python:3.10.5-alpine3.16

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update \
    && apk add --no-cache postgresql-dev \
    gcc \
    cargo \
    python3 \
    musl-dev \
    jpeg-dev \
    zlib-dev \
    tiff-dev \
    libjpeg-turbo-dev \
    libffi-dev \
    openssl-dev

COPY . /app

RUN pip install --upgrade pip
RUN pip install -r app/requirements.txt

WORKDIR /app