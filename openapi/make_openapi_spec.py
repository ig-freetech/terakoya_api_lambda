import os

openapi_dpath = os.path.dirname(__file__)

with open(os.path.join(openapi_dpath, "openapi_template.yml"), "r") as f:
    content = f.read()

# Replace ${VAR} with actual environment variable value
content = os.path.expandvars(content)

with open(os.path.join(openapi_dpath, "openapi.yml"), "w") as f:
    f.write(content)
