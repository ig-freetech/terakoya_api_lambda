# HACK: Lambdaコンテナのベースイメージが 2022 を使っていたので合わせる
FROM amazonlinux:2022

RUN yum update -y && \
    yum install -y gcc wget zip tar gzip make openssl-devel bzip2-devel libffi-devel zlib-devel sqlite-devel git && \
    cd /opt && \
    wget https://www.python.org/ftp/python/3.9.12/Python-3.9.12.tgz && \
    tar xzf Python-3.9.12.tgz && \
    /opt/Python-3.9.12/configure --enable-optimizations && \
    make altinstall && \
    rm -f /opt/Python-3.9.12.tgz && \
    python3.9 -m pip install --upgrade pip

# ソースコードでは使用しないが開発環境では必要なライブラリのインストール
RUN pip install autopep8 pytest

# Install Nodejs on Amazon Linux 2
# https://docs.aws.amazon.com/sdk-for-javascript/v2/developer-guide/setting-up-node-on-ec2-instance.html
# RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash && \
#     . ~/.nvm/nvm.sh && nvm install --lts && \
#     # Install serverless cli via npm
#     # https://www.serverless.com/framework/docs/getting-started
#     npm install -g serverless

# Install Node.js to run serverless framework
# https://qiita.com/3582/items/31a9a98325b7f205d009
# Add Node.js 16.x repository to yum
# RUN curl -fsSL https://rpm.nodesource.com/setup_16.x | bash - && \
#     yum install -y nodejs npm && \
#     # https://www.serverless.com/framework/docs/getting-started
#     npm install -g serverless

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

# WARNING: なぜかパッケージがインストールされない。イメージ作成時にはマウントディレクトリにパッケージをインストールできない？ 仕方ないのでパッケージインストールの度にコンテナ側で下記コマンドを打って対応
# RUN pip install -r requirements.txt -t ./functions/python
ENV PYTHONPATH $PYTHONPATH:./functions/python

# Set environment variables for development
ENV STAGE dev