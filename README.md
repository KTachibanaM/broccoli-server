# broccoli-platform
🥦, a web content crawling and sorting platform

View `README.md`s in `broccoli`, `broccoli-web` and `herr-ashi` to get started

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
This is a set of services and webapps that generalize the crawling, processing, sorting and publishing of Internet content, while offer pluggability so that you customize it to fulfill individual use cases

## Components
* `server`: The backend server that serves the content repository. It exposes a set of RPC actions, via AMQP and HTTP, to query and manipulate the content repository
* `worker_manager`: The backend server that schedules and runs workers which query and manipulate the content repository. It exposes a declarative API for end users to schedule workers
* `api`: The backend server that hosts information about the content management dashboards. It additionally exposes a configurable selected portion of the content repository to the public Internet
* `broccoli-web`: The frontend webapp that mainly displays the content management dashboards and additionally offers the UI to schedule the workers
