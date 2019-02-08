FROM python:3.7.2

COPY . /app
WORKDIR /app

RUN pip install pipenv && pipenv install --system --deploy

CMD ["python", "server.py"]