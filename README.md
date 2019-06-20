# broccoli-server
[![Build Status](https://travis-ci.org/broccoli-platform/broccoli-server.svg?branch=master)](https://travis-ci.org/broccoli-platform/broccoli-server)

The server component of a web content crawling and sorting platform

## Problem Statement
* I want to
    * Crawl content, such as images and texts, from "feeds" on the Internet, such as RSS, Twitter, some random webpage
    * Archive those content into a centralized repository
    * Process the content and attach extra attributes, such as extracting hash, width, height of an image, or translating a piece of text
    * Manage the content repository using a dashboard, such as viewing images and duplicates, or viewing texts and changing their translation
    * Expose the content repository to the world with certain attributes, such as "moderation is true"
* While I do not want to
    * Re-implement crawling resiliency and failure observability for different use cases
    * Specify different programming language object models for content in different use cases
    * Re-implement common elements in a management dashboard for different use cases

## Solution
This is an application that generalizes the crawling, processing, sorting and publishing of Internet content, while offer pluggability so that you customize it to fulfill individual use cases

## Architecture
* There is a server application that does the heavy-lifting of crawling and processing of Internet content. Those activities can also be queried and changed via HTTP endpoints.
* The server application also stores metadata about the user interfaces it should be exposing for the purpose of human moderation.
* The server application also exposes HTTP endpoints to publish the repository of Internet content.
* The server application stores its state (for example, the repository of Internet content) to a database.
* There is a web application that uses the server HTTP endpoints and allows end users to query and control crawling and processing activities.
* The web application also displays user interfaces for human moderation, according to the metadata stored by the server.
* The architecture is currently not multi-tenant, meaning there is only one single-purposed repository of Internet content that a pair of server application + web application + database instance can serve.

## Concepts and Pluggability
* A worker is a "cron" job object that runs within the server application and reads/writes to the repository of Internet content.
* Worker classes ("class" as in OOP) are registered to the server application at runtime and thus pluggable.
* Worker objects are instantiated and run within the server application at runtime according to worker metadata, which can also be queried and changed at runtime.
* An API handler is an object that handles public query traffic to the repository of Internet content in HTTP.
* API handler classes ("class" as in OOP) are registered to the server application at runtime and thus pluggable.
* API handler objects are registered within the server application at runtime according to static configuration.
* A board is an user interface that allows end users to view and manipulate the repository of Internet content.
* A board shows rows, each row corresponds to an entry in the repository of Internet content.
* What rows to show, how many rows to show, in what order the rows are shown, are controlled by the metadata of each board.
* A row have columns. What to show for each column is also controlled by the metadata of each board.
* How to actually show each column is encoded within `weblets`, sets of runtime-pluggable JS functions that takes in an entry of the repository of Internet content and outputs a React component.

## Prerequisites
* `Python 3.7`
* `pipenv`
* `Node.js`
* `MongoDB`
    * Have an unauthenticated MongoDB running at `localhost:27017`
        * macOS
        ```bash
        brew install mongodb
        brew services start mongodb
        ```
        * Debian and Ubuntu: Follow [this guide](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/)
    * To verify, run the `mongo` in your terminal and you should be dropped to a MongoDB interactive shell

## Getting Started
* Follow `README.md` on `broccoli-dev-tools` to get an instance (or multiple) of `broccoli-platform` running
