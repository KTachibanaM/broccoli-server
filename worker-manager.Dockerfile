FROM python:3.7

COPY ./broccoli-common /app/broccoli-common
COPY ./broccoli-plugin-interface /app/broccoli-plugin-interface
COPY ./broccoli-worker-manager /app/broccoli-worker-manager

WORKDIR /app/broccoli-worker-manager
RUN pip install pipenv
RUN pipenv install --system --deploy
RUN pip install pip==18.1

ENV FLASK_ENV=production
ENV BPI_DEP_LINK=git+file:///app/broccoli-plugin-interface#egg=broccoli_plugin_interface
EXPOSE 5002
CMD ["sh", "-c", "./install_plugin.container.sh && python worker_manager.py"]
