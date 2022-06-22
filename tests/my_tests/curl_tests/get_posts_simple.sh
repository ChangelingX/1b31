#!/bin/bash
CURL_JSON_API_TOKEN=$(cat /workspaces/1b31/tests/my_tests/curl_tests/token.cred)
curl --location --request GET 'localhost:5000/api/posts' \
--header "x-access-token: $CURL_JSON_API_TOKEN" \
--data-raw '{
    "authorIds": "1,5",
    "sortBy": "id",
    "direction": "asc"
}'