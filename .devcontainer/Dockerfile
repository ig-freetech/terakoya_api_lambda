# Lambda container image is amazonlinux:2022
FROM amazonlinux:2022

RUN yum update -y && \
    yum install -y gcc wget zip tar gzip make openssl-devel bzip2-devel libffi-devel zlib-devel sqlite-devel git curl && \
    cd /opt && \
    wget https://www.python.org/ftp/python/3.9.12/Python-3.9.12.tgz && \
    tar xzf Python-3.9.12.tgz && \
    /opt/Python-3.9.12/configure --enable-optimizations && \
    make altinstall && \
    rm -f /opt/Python-3.9.12.tgz && \
    python3.9 -m pip install --upgrade pip

# Install packages for functions
COPY ./functions/requirements.txt ./functions/requirements.txt
# Use --no-cache-dir to install packages strictly based on requirements.txt without cache every time
# https://daeudaeu.com/pip-no-cache-dir/
RUN pip install --no-cache-dir -r ./functions/requirements.txt -t ./functions/layer/python
# Add layer path to PYTHONPATH to import modules in layer that packages are installed above
ENV PYTHONPATH $PYTHONPATH:./functions/layer/python

# Install packages for testing
COPY ./tests/requirements.txt ./tests/requirements.txt
RUN pip install --no-cache-dir -r ./tests/requirements.txt

# Install packages for development and testing that are not needed in production
# https://docs.pytest.org/en/7.1.x/getting-started.html
RUN pip install autopep8

# Copy aws credentials to use AWS toolkit extension
# https://docs.aws.amazon.com/ja_jp/cli/latest/userguide/cli-configure-files.html
COPY ./.aws /root/.aws

# Set environment variables for local
ENV STAGE dev