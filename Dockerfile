from python:3.12-alpine

WORKDIR /
COPY requirements.txt /requirements.txt

RUN python3 -m pip install -r requirements.txt
ENTRYPOINT python3 /code/sc_code.py