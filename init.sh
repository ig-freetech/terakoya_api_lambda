rm -rf ./functions/layer/python
# -t <dir_path> makes the directories recursively if any directories do not exist and installs the packages in the directory.
pip install --no-cache-dir -r ./functions/requirements.txt -t ./functions/layer/python