#!/bin/sh
curl --location --request GET 'localhost:5000/api/posts' \
--header 'Content-Type: application/json' \
--data-raw '{
    "sortBy": "id",
    "direction": "asc"
}'