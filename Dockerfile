FROM nikolaik/python-nodejs:python3.7-nodejs11

# Copy over here
COPY . /app

# Install server dependencies
WORKDIR /app/server
RUN pipenv install --deploy --system

# Install server plugin
WORKDIR /app
ARG SERVER_PLUGIN
ENV BPI_DEP_LINK=git+file:///app/broccoli-plugin-interface#egg=broccoli_plugin_interface
RUN pip install pip==18.1
RUN pip install $SERVER_PLUGIN --process-dependency-links

# Install web dependencies
WORKDIR /app/web
RUN npm install

# Build web
WORKDIR /app
ARG PUBLIC_URL
ARG REACT_APP_SERVER_URL
RUN ./build_web.sh

WORKDIR /app/server
ENV FLASK_ENV=production
CMD ["python", "app.py"]