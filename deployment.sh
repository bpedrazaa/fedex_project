#!/bin/bash
DEPLOYMENT_BUCKET="destination2-upb-1010"

while getopts ":bdpw" OPTION; do
    case $OPTION in
    w)
      WEBSITE=1
      ;;
    d)
      DEPLOY=1
      ;;
    p)
      PACKAGE=1
      ;;
    b)
      BUILD=1
      ;;
    *)
      ;;
    esac
done

if [[ $BUILD == 1 ]]
then
    pip3 install --target package -r requirements.txt
    cp -a src/. package/
    # zip -r9 ../function.zip .
    # cd ../src
    # zip -g ../function.zip *
fi

if [[ $PACKAGE == 1 ]]
then
    aws cloudformation package --template-file fedex_template.yaml --s3-bucket $DEPLOYMENT_BUCKET --output-template-file packaged-template.json
fi

if [[ $DEPLOY == 1 ]]
then
    aws cloudformation deploy --template-file packaged-template.json --stack-name upb-fedex-project --capabilities CAPABILITY_NAMED_IAM
fi

if [[ $WEBSITE == 1 ]]
then
    WEBSITE_BUCKET_PATH="/fedex/s3bucket"
    WEBSITE_BUCKET=$(aws ssm get-parameters --names $WEBSITE_BUCKET_PATH --query "Parameters[0].Value" | tr -d '"')
    aws s3 cp index.html s3://$WEBSITE_BUCKET/    
fi