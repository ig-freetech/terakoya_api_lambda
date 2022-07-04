# ZIP ファイル化

`zip -r functions.zip ./functions -x '*python*'`
`zip -r python.zip ./functions/python'`

# S3 へアップロード

`aws s3 cp ./functions.zip s3://ig-general/lambda/`
`aws s3 cp ./python.zip s3://ig-general/lambda/`

# S3 Bucket URI (lambda 関数のアップロード元)

`s3://ig-general/lambda/functions.zip`
`s3://ig-general/lambda/python.zip`
