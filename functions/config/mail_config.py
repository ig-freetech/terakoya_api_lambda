import os
# TODO: Comment out the following line in Lambda console after deployment
from dotenv import load_dotenv
load_dotenv()

TERAKOYA_GMAIL_ADDRESS = os.getenv("TERAKOYA_GMAIL_ADDRESS")
TERAKOYA_GROUP_MAIL_ADDRESS = os.getenv("TERAKOYA_GROUP_MAIL_ADDRESS")
