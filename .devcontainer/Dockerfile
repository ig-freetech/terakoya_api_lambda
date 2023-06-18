# Lambda container image is amazonlinux:2022
FROM amazonlinux:2022

# https://www.python.org/downloads/
RUN yum update -y && \
    yum install -y gcc wget zip tar gzip make openssl-devel bzip2-devel libffi-devel zlib-devel sqlite-devel git && \
    cd /opt && \
    wget https://www.python.org/ftp/python/3.9.16/Python-3.9.16.tgz && \
    tar xzf Python-3.9.16.tgz && \
    /opt/Python-3.9.16/configure --enable-optimizations && \
    make altinstall && \
    rm -f /opt/Python-3.9.16.tgz && \
    python3.9 -m pip install --upgrade pip

# Current working directory is / (root) by default when Dockerfile is built and each commands (ex: RUN, COPY) are executed.
# https://christina04.hatenablog.com/entry/2014/10/31/101510
WORKDIR /workspaces/terakoya_backend

# Install packages for production
COPY ./functions/requirements.txt ./functions/requirements.txt

# mkdir -p <dir_path> creates directories recursively and does not throw an error if the directory already exists.
# https://cns-guide.sfc.keio.ac.jp/2001/3/3/5.html
# https://blog.katty.in/4967#toc5
# RUN mkdir -p ./functions/layer/python && \
#     # Use --no-cache-dir to install packages strictly based on requirements.txt without cache every time
#     # https://daeudaeu.com/pip-no-cache-dir/
#     pip install --no-cache-dir -r ./functions/requirements.txt -t ./functions/layer/python

# Add layer path to PYTHONPATH to import modules in layer that packages are installed above
ENV PYTHONPATH $PYTHONPATH:/workspaces/terakoya_backend/functions/layer/python

# Install packages for testing
COPY ./tests/requirements.txt ./tests/requirements.txt
RUN pip install --no-cache-dir -r ./tests/requirements.txt

# Install packages for development that are not needed in production
# uvicorn works as a ASGI server to run FastAPI on local
# https://www.uvicorn.org/
RUN pip install autopep8 uvicorn

# Copy aws credentials to use AWS toolkit extension
# https://docs.aws.amazon.com/ja_jp/cli/latest/userguide/cli-configure-files.html
COPY ./.aws /root/.aws

# Set environment variables for local
ENV STAGE dev