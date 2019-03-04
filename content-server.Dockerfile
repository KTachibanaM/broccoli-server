FROM python:3.7

COPY ./broccoli-common /app/broccoli-common
COPY ./broccoli-content-server /app/broccoli-content-server

WORKDIR /app/broccoli-content-server
RUN pip install pipenv
RUN pipenv install --system --deploy

ENV FLASK_ENV=development
EXPOSE 5000
CMD ["python", "content_server.py"]
