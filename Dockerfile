# Необходимо использовать свой базовый образ
FROM python:3.12.4-slim-bookworm as builder

COPY .ci-cd/pip.conf /etc/pip.conf

WORKDIR /tmp

COPY requirements.txt .

RUN echo \
    "deb http://mirror.yandex.ru/debian bookworm main\n" \
    "deb http://mirror.yandex.ru/debian-security bookworm-security main\n" \
    "deb http://mirror.yandex.ru/debian bookworm-updates main\n" > /etc/apt/sources.list \
    && apt-get update && apt-get install -y gcc

RUN pip install -U pip && pip install --user --no-cache-dir -r requirements.txt

FROM python:3.12.4-slim-bookworm

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /code

COPY --from=builder /root/.local /root/.local
# Чтобы скрипты, которые устанавливаются с библиотеками
# (типа uvicorn), были в PATH.
ENV PATH=/root/.local/bin:$PATH

COPY . .

EXPOSE 8000

ARG VERSION
ENV VERSION=${VERSION}