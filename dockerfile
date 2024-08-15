FROM python:3.12-slim

WORKDIR /code/neu

RUN apt update \
    && apt upgrade -y \
    && apt install git -y \
    && apt autoremove -y \
    && apt clean -y

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir --upgrade pip setuptools \
    && pip install --no-cache-dir -r requirements.txt

COPY src src

CMD ["python", "src/main.py" ]
