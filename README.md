# ZIP ファイル化

`zip -r functions.zip ./functions -x '*python*'`

# S3 へアップロード

`aws s3 cp ./functions.zip s3://ig-general/lambda/`
