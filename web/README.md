# broccoli-web
The frontend of a web content crawling and sorting platform

## Prerequisites
* `Node.js`
* `yarn`

## Build
```bash
yarn install
yarn build
```

## Run
This is a static frontend and shouldn't be served standalone
because the code assumes the static artifacts will be served under `/web` HTTP path of a `broccoli-server` instance
