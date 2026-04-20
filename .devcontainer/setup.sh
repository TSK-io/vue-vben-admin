#!/bin/bash
set -e # 遇到错误立即停止执行

echo "开始更新软件包列表..."
sudo apt-get update

echo "正在安装系统工具..."
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    ripgrep \
    fd-find \
    bat \
    fzf \
    jq \
    tree \
    ncdu \
    lsof \
    iproute2 \
    procps \
    netcat-openbsd \
    dnsutils \
    less \
    unzip

echo "配置命令别名 (fd, bat)..."
sudo ln -sf /usr/bin/fdfind /usr/local/bin/fd
sudo ln -sf /usr/bin/batcat /usr/local/bin/bat

echo "清理缓存..."
sudo apt-get clean
sudo rm -rf /var/lib/apt/lists/*

echo "配置 Node.js 环境..."
corepack enable

# 【关键点】禁用 Corepack 的交互式下载确认，防止卡死
export COREPACK_ENABLE_DOWNLOAD_PROMPT=0

echo "验证版本信息:"
pnpm --version
python3 --version

echo "✅ 所有初始化任务已完成！"
