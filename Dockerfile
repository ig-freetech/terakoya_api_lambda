# FROM python:3.9-buster as builder
# RUN mkdir packages
# WORKDIR /packages
# COPY ./functions/requirements.txt /packages/
# RUN pip install -U pip && pip install -r requirements.txt

# FROM python:3.9-slim-buster as production
# COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages/
# COPY ./functions /functions
# WORKDIR /functions
# CMD /bin/bash

# HACK: Lambdaコンテナのベースイメージが 2022 を使っていたので合わせる
FROM amazonlinux:2022
RUN yum update -y && \
    yum install -y gcc wget zip tar gzip make openssl-devel bzip2-devel libffi-devel zlib-devel sqlite-devel && \
    cd /opt && \
    wget https://www.python.org/ftp/python/3.9.12/Python-3.9.12.tgz && \
    tar xzf Python-3.9.12.tgz && \
    /opt/Python-3.9.12/configure --enable-optimizations && \
    make altinstall && \
    rm -f /opt/Python-3.9.12.tgz && \
    python3.9 -m pip install --upgrade pip
# 開発用ライブラリのインストール
RUN pip install autopep8 
    
COPY ./functions /functions/
WORKDIR /functions
# WARNING: なぜかパッケージがインストールされない。イメージ作成時にはマウントディレクトリにパッケージをインストールできない？ ひとまず初回だけコンテナ側で下記コマンドを打って対応
# RUN pip install -r requirements.txt -t ./python
ENV PYTHONPATH $PYTHONPATH:/functions/python
CMD ["/bin/bash"]