FROM ubuntu:18.04

# Install Python 3.7 and Node 11
RUN apt-get update && \
    apt-get install -y software-properties-common curl gnupg git && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt-get install -y python3.7 && \
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python3.7 get-pip.py && \
    curl -sL https://deb.nodesource.com/setup_11.x | bash - && \
    apt-get install -y nodejs

# Copy over here
COPY . /app
WORKDIR /app

# Install server dependencies
WORKDIR /app/server
RUN pip install pipenv
RUN pip install pip==18.1
RUN pipenv install --system --deploy

# Install web dependencies
WORKDIR /app/web
RUN npm install

WORKDIR /app
ENV FLASK_ENV=production
ENV BPI_DEP_LINK=git+file:///app/broccoli-plugin-interface#egg=broccoli_plugin_interface
CMD ["sh", "-c", "./install_server_plugin.sh && ./build_web.sh && cd /app/server && python3.7 app.py"]