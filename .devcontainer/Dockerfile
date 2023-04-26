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

# Install Node.js to run serverless framework
# https://qiita.com/3582/items/31a9a98325b7f205d009
# Add Node.js 16.x repository to yum
# RUN curl -fsSL https://rpm.nodesource.com/setup_16.x | bash - && \
#     yum install -y nodejs npm && \
#     # https://www.serverless.com/framework/docs/getting-started
#     npm install -g serverless

# WARNING: なぜかパッケージがインストールされない。イメージ作成時にはマウントディレクトリにパッケージをインストールできない？ 仕方ないのでパッケージインストールの度にコンテナ側で下記コマンドを打って対応
# RUN pip install -r requirements.txt -t ./python
ENV PYTHONPATH $PYTHONPATH:./functions/python