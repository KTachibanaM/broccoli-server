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

curl --request POST \
  --url http://localhost:5001/board/dedup \
  --header 'content-type: application/json' \
  --data '{
	"q": {
		"pending_removal": {
			"$exists": false
		},
		"image_dhash": {
			"$exists": true
		},
		"unique": {
			"$exists": false
		}
	},
	"projections": [
		{
			"args": [],
			"js_filename": "image",
			"name": "Image"
		},
		{
			"args": [],
			"js_filename": "dupImages",
			"name": "Dups"
		}
	]
}'

curl --request POST \
  --url http://localhost:5001/board/mod \
  --header 'content-type: application/json' \
  --data '{
	"q": {
		"pending_removal": {
			"$exists": false
		},
		"mod": {
			"$exists": false
		},
		"unique": true
	},
	"projections": [
		{
			"args": [],
			"js_filename": "image",
			"name": "Image"
		}
	]
}'

curl --request POST \
  --url http://localhost:5001/board/public \
  --header 'content-type: application/json' \
  --data '{
	"q": {
		"pending_removal": {
			"$exists": false
		},
		"mod": true
	},
	"projections": [
		{
			"args": [],
			"js_filename": "image",
			"name": "Image"
		}
	]
}'

curl --request POST \
  --url http://localhost:5001/board/pending_removal \
  --header 'content-type: application/json' \
  --data '{
	"q": {
		"pending_removal": true
	},
	"projections": [
		{
			"args": [],
			"js_filename": "image",
			"name": "Image"
		}
	]
}'
