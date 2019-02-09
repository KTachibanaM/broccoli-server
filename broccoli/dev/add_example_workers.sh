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

curl --request POST \
  --url http://localhost:5002/api/worker \
  --header 'content-type: application/json' \
  --data '{
	"module": "workers.twitter_image_backfiller",
	"class_name": "TwitterImageBackfiller",
	"args": {
	     "screen_name": "Wzettairyouiki",
	     "init_tweet_id": 1094105684180897792,
	     "round_count": 10,
	     "pause_after_round": 1
	},
	"global_args": [],
    "interval_seconds": 30
}'
