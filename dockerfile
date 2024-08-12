FROM python:3.12-slim

WORKDIR /code/neu

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir --upgrade pip setuptools \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["fastapi", "run", "src/main.py",  "--proxy-headers", "--port", "80"]
