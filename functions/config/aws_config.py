import os
from dotenv import load_dotenv
load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("ACCESS_KEY")
AWS_SECRET_ACCESS_KEY = os.getenv("SECRET_ACCESS_KEY")
AWS_DEFAULT_REGION = os.getenv("DEFAULT_REGION")

# SES
SES_TEST_ADDRESS_1 = os.getenv("SES_TEST_ADDRESS_1")
SES_TEST_ADDRESS_2 = os.getenv("SES_TEST_ADDRESS_2")
