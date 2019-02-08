#!/usr/bin/env bash

curl --request POST \
  --url http://localhost:5002/api/worker \
  --header 'content-type: application/json' \
  --data '{
	"module": "workers.lofter_image_scraper",
	"class_name": "LofterImageScraper",
	"args": {
		 "subdomain": "ywazwww"
	},
	"global_args": [],
	"interval_seconds": 60
}'

curl --request POST \
  --url http://localhost:5002/api/worker \
  --header 'content-type: application/json' \
  --data '{
	"module": "workers.s3_image_hoarder",
	"class_name": "S3ImageHoarder",
	"args": {},
	"global_args": ["image_s3"],
    "interval_seconds": 30
}'

curl --request POST \
  --url http://localhost:5002/api/worker \
  --header 'content-type: application/json' \
  --data '{
	"module": "workers.image_hash_tagger",
	"class_name": "ImageHashTagger",
	"args": {},
	"global_args": ["image_s3"],
    "interval_seconds": 30
}'
