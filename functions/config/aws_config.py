import os
# TODO: Comment out the following line in Lambda console after deployment
from dotenv import load_dotenv
load_dotenv()

# https://docs.aws.amazon.com/ja_jp/lambda/latest/dg/configuration-envvars.html

AWS_ACCESS_KEY_ID = os.getenv("ACCESS_KEY")
AWS_SECRET_ACCESS_KEY = os.getenv("SECRET_ACCESS_KEY")
AWS_DEFAULT_REGION = os.getenv("DEFAULT_REGION")

# SES
SES_TEST_ADDRESS_1 = os.getenv("SES_TEST_ADDRESS_1")
SES_TEST_ADDRESS_2 = os.getenv("SES_TEST_ADDRESS_2")

# Dynamo DB
DYNAMO_DB_BOOKING_TABLE = os.getenv("DYNAMO_DB_BOOKING_TABLE")
