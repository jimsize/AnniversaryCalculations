#!/usr/bin/env bash

# Update the AWS Lambda function for the Anniversary Message project.
thisdir="$(dirname "$0")"
aws lambda update-function-code \
    --function-name AnniversaryMessage \
    --zip-file "fileb://$thisdir/dist/anniversary.zip"
