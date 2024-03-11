FROM python:3.11
LABEL authors="srikeerthanred.aluri"

WORKDIR /code

COPY requirements.txt /code/requirements.txt
COPY .env /code/.env
COPY version.py /code/version.py

RUN pip install uvicorn

RUN pip install --no-cache-dir -r /code/requirements.txt

COPY ./app /code/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]