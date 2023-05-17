import os

# https://docs.aws.amazon.com/ja_jp/lambda/latest/dg/configuration-envvars.html

AWS_ACCESS_KEY_ID = os.getenv("ACCESS_KEY")
AWS_SECRET_ACCESS_KEY = os.getenv("SECRET_ACCESS_KEY")
AWS_DEFAULT_REGION = os.getenv("DEFAULT_REGION")

TERAKOYA_GMAIL_ADDRESS = os.getenv("TERAKOYA_GMAIL_ADDRESS")
TERAKOYA_GROUP_MAIL_ADDRESS = os.getenv("TERAKOYA_GROUP_MAIL_ADDRESS")

STAGE = os.getenv("STAGE")
