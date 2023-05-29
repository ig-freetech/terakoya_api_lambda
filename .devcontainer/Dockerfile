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

# Install packages for development and testing that are not needed in production
# https://docs.pytest.org/en/7.1.x/getting-started.html
RUN pip install autopep8

# Install packages for testing
COPY ./tests/requirements.txt ./tests/requirements.txt
RUN pip install --no-cache-dir -r ./tests/requirements.txt

# moto is a library that allows your python tests to easily mock out the boto library
# https://obataka.com/moto-dynamodb/
# https://qiita.com/abemaru/items/7a521a8cf6d755c0f34c
# RUN pip install autopep8 pytest pytest-freezegun moto

# Copy aws credentials to use AWS toolkit extension
# https://docs.aws.amazon.com/ja_jp/cli/latest/userguide/cli-configure-files.html
COPY ./.aws /root/.aws

# Install gh cli to set secrets
# https://github.com/cli/cli/blob/trunk/docs/install_linux.md#amazon-linux-2-yum
# command A || command B means if command A fails, run command B
# https://qiita.com/arene-calix/items/41d8d4ba572f1d652727#--
# RUN yum install -y yum-utils && \
#     yum-config-manager --add-repo https://cli.github.com/packages/rpm/gh-cli.repo && \
#     yum install -y gh && yum update gh
# TODO: Need to run `gh auth login` to use gh cli every time when container is created
# https://cli.github.com/manual/gh_auth_login
# https://cli.github.com/manual/

COPY ./functions/requirements.txt ./functions/requirements.txt
# Use --no-cache-dir to install packages strictly based on requirements.txt without cache every time
# https://daeudaeu.com/pip-no-cache-dir/
RUN pip install --no-cache-dir -r ./functions/requirements.txt -t ./functions/layer/python
ENV PYTHONPATH $PYTHONPATH:./functions/layer/python

# Set environment variables for local
ENV STAGE dev