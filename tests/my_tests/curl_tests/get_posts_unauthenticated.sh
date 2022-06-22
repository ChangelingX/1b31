#!/bin/bash
curl --location --request GET 'localhost:5000/api/posts' \
--header 'Content-Type: application/json' \
--data-raw '{
    "authorIds": "1,5",
    "sortBy": "id",
    "direction": "asc"
}'