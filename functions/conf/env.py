import os

# https://docs.aws.amazon.com/ja_jp/lambda/latest/dg/configuration-envvars.html

AWS_ACCESS_KEY_ID = os.getenv("ACCESS_KEY")
AWS_SECRET_ACCESS_KEY = os.getenv("SECRET_ACCESS_KEY")
# DEFAULT_REGION is used in Lambda's runtime environment but AWS_DEFAULT_REGION is used via .env
# https://docs.aws.amazon.com/ja_jp/lambda/latest/dg/configuration-envvars.html#configuration-envvars-runtime
AWS_DEFAULT_REGION = os.getenv("DEFAULT_REGION") if os.getenv("DEFAULT_REGION") else os.getenv("AWS_DEFAULT_REGION")

TERAKOYA_GMAIL_ADDRESS = os.getenv("TERAKOYA_GMAIL_ADDRESS")
TERAKOYA_GROUP_MAIL_ADDRESS = os.getenv("TERAKOYA_GROUP_MAIL_ADDRESS")

STAGE = os.getenv("STAGE")

# GATEWAY_ID is not defined in local environment, so use GATEWAY_ID_DEV in .env loaded by .devcontainer
GATEWAY_ID = os.getenv("GATEWAY_ID") if os.getenv("GATEWAY_ID") else os.getenv("GATEWAY_ID_DEV")
