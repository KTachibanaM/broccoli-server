FROM ubuntu:18.04

RUN apt-get update && \
    apt-get install -y curl gnupg && \
    curl -sL https://deb.nodesource.com/setup_11.x | bash - && \
    apt-get install -y nodejs

COPY . /app
WORKDIR /app
RUN npm install

EXPOSE 3000
CMD ["sh", "-c", "./inject_environment.container.sh && npm run start"]
