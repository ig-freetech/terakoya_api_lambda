FROM amazonlinux:2022

# Install sqlite3
RUN yum update && cd root && \
    # Install tools for build
    yum install -y wget tar gzip gcc make && \
    # Get source
    wget https://www.sqlite.org/2022/sqlite-autoconf-3400100.tar.gz && \
    # Unzip and extract
    tar xvfz sqlite-autoconf-3400100.tar.gz && \
    # Build and install
    cd sqlite-autoconf-3400100 && ./configure --prefix=/usr/local && make && make install && \
    # Check install finished
    sqlite3 --version