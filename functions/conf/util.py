# Relative import
# https://note.nkmk.me/python-relative-import/
from .env import STAGE

IS_PROD = STAGE == "prod"
