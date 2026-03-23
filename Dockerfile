FROM python:3.12-slim

# 基本ツールのインストール
RUN apt-get update && apt-get install -y \
    unixodbc-dev \
    gcc \
    g++ \
    curl \

    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Microsoftの鍵を保存するディレクトリを作成し、鍵を安全な形式で保存
RUN mkdir -p /etc/apt/keyrings \
    && curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /etc/apt/keyrings/microsoft.gpg

# リポジトリの設定（Driver 17が含まれる Debian 11 "bullseye" 用を指定）
RUN echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/11/prod bullseye main" > /etc/apt/sources.list.d/mssql-release.list

# ODBCドライバーのインストール（最新の v18 を指定）
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17

# 日本語に強くする
RUN apt-get update && apt-get install -y locales \
    && locale-gen ja_JP.UTF-8
ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:jp
ENV LC_ALL ja_JP.UTF-8

# 必要なライブラリのインストール
RUN pip install --no-cache-dir \
    pyodbc \
    pandas \
    openpyxl \
    zenhan \
    pdfplumber

WORKDIR /app
