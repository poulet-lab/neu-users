FROM python:3.12-alpine AS builder

RUN apk --no-cache update && \
    apk --no-cache upgrade && \
    apk --no-cache add  git

RUN  pip install --no-cache-dir --upgrade pip setuptools

WORKDIR /neu

COPY . .

RUN pip install --no-cache-dir .

CMD ["python", "neu_users/main.py" ]
