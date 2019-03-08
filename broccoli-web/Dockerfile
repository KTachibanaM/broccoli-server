FROM ubuntu:18.04

RUN apt-get update && \
    apt-get install -y curl gnupg && \
    curl -sL https://deb.nodesource.com/setup_11.x | bash - && \
    apt-get install -y nodejs

COPY . /app
WORKDIR /app
RUN npm install
RUN npm install -g serve

EXPOSE 5000
CMD ["sh", "-c", "./inject_environment.container.sh && npm run build && serve /app/build"]
