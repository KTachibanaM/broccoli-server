FROM nikolaik/python-nodejs:python3.7-nodejs11

# Copy over here
COPY . /app

# Install server dependencies
WORKDIR /app/server
RUN pipenv install --deploy --system

# Install web dependencies
WORKDIR /app/web
RUN npm install

WORKDIR /app
ENV FLASK_ENV=production
ENV BPI_DEP_LINK=git+file:///app/broccoli-plugin-interface#egg=broccoli_plugin_interface
EXPOSE 5000
CMD ["sh", "-c", "./install_server_plugin.sh && ./build_web.sh && cd /app/server && python app.py"]