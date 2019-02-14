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
	     "round_count": 5,
	     "pause_after_round": 2
	},
	"global_args": [],
    "interval_seconds": 30
}'

curl --request POST \
  --url http://localhost:5002/api/worker \
  --header 'content-type: application/json' \
  --data '{
	"module": "workers.twitter_image_scraper",
	"class_name": "TwitterImageScraper",
	"args": {
	     "screen_name": "Wzettairyouiki"
	},
	"global_args": [],
    "interval_seconds": 60
}'

curl --request POST \
  --url http://localhost:5001/board/mod \
  --header 'content-type: application/json' \
  --data '{
	"q": {
		"image_dhash": {
			"$exists": true
		},
		"mod": {
			"$exists": false
		}
	},
	"sort": {
	    "created_at": 1
	},
	"projections": [
		{
            "name": "Image",
            "js_filename": "image",
			"args": []
		},
		{
            "name": "Duplicate images",
            "js_filename": "dupImages",
			"args": []
		},
		{
            "name": "Approve",
            "js_filename": "updateOneButton",
			"args": ["Approve", "s3_image_id", {"mod": true}]
		},
		{
            "name": "Disapprove",
            "js_filename": "updateOneButton",
			"args": ["Disapprove", "s3_image_id", {"mod": false, "mod_false_reason": "disapprove"}]
		},
		{
            "name": "Is duplicate",
            "js_filename": "updateOneButton",
			"args": ["Is duplicate", "s3_image_id", {"mod": false, "mod_false_reason": "duplicate"}]
		}
	]
}'

curl --request POST \
  --url http://localhost:5001/board/public \
  --header 'content-type: application/json' \
  --data '{
	"q": {
		"mod": true
	},
	"projections": [
		{
            "name": "Image",
            "js_filename": "image",
			"args": []
		}
	]
}'

curl --request POST \
  --url http://localhost:5001/board/mod_false \
  --header 'content-type: application/json' \
  --data '{
	"q": {
		"mod": false
	},
	"projections": [
		{
            "name": "Image",
            "js_filename": "image",
			"args": []
		},
		{
            "name": "mod_false_reason",
            "js_filename": "echo",
			"args": ["mod_false_reason"]
		}
	]
}'
