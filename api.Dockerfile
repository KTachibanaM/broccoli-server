FROM python:3.7

COPY ./broccoli-common /app/broccoli-common
COPY ./broccoli-plugin-interface /app/broccoli-plugin-interface
COPY ./broccoli-api /app/broccoli-api

WORKDIR /app/broccoli-api
RUN pip install pipenv
RUN pipenv install --system --deploy
RUN pip install pip==18.1

ENV FLASK_ENV=production
EXPOSE 5001
CMD ["sh", "-c", "./install_plugin_container.sh && python api.py"]
