# ZIP ファイル化

`zip -r functions.zip ./functions -x '*python*'`
`zip -r functions_dev.zip ./functions -x '*python*'`
`zip -r layer.zip ./functions/python`
`zip index.zip ./functions/index.py`

# S3 へアップロード

`aws s3 cp ./functions.zip s3://ig-general/lambda/`
`aws s3 cp ./functions_dev.zip s3://ig-general/lambda/`
`aws s3 cp ./layer.zip s3://ig-general/lambda/`

# S3 Bucket URI (lambda 関数のアップロード元)

`s3://ig-general/lambda/functions.zip`
`s3://ig-general/lambda/python.zip`

# ハンドラ設定

`functions/book.lambda_handler`
`functions/remind.lambda_handler`
