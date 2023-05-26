import os
import toml

pyproject_dpath = os.path.dirname(__file__)
tests_dpath = os.path.dirname(pyproject_dpath)
config = toml.load(os.path.join(pyproject_dpath, "pyproject_template.toml"))

# Update the settings with environment variables
config["tool"]["pytest"]["ini_options"]["slack_hookurl"] = os.getenv("SLACK_ERROR_CH_WEBHOOK_URL")
config["tool"]["pytest"]["ini_options"]["slack_channel"] = os.getenv("SLACK_ERROR_CH_NAME")

# Write the updated settings back to a new file
with open(os.path.join(tests_dpath, "pyproject.toml"), "w") as f:
    toml.dump(config, f)
