#!/bin/bash
#https://stackoverflow.com/questions/28971771/getting-json-value-from-curl-in-linux-bash
content=$(curl --location --request POST 'localhost:5000/api/login' \
--header 'Content-Type: application/json' \
--data-raw '{
    "username": "thomas",
    "password": "123456"
}')
token=$(jq -r '.token'<<<"$content")
echo "$token" > /workspaces/1b31/tests/my_tests/curl_tests/token.cred