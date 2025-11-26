#!/bin/bash

# 智能投资助手后端部署脚本
echo "开始部署智能投资助手后端..."

# 检查Node.js环境
if ! command -v node &> /dev/null; then
    echo "错误: 未找到Node.js。请先安装Node.js 16+"
    exit 1
fi

# 检查npm环境
if ! command -v npm &> /dev/null; then
    echo "错误: 未找到npm。请先安装npm 7+"
    exit 1
fi

echo "Node.js版本: $(node -v)"
echo "npm版本: $(npm -v)"

# 安装依赖
echo "正在安装依赖..."
npm install --production

if [ $? -ne 0 ]; then
    echo "错误: 依赖安装失败"
    exit 1
fi

# 创建环境变量文件
if [ ! -f .env ]; then
    echo "创建.env配置文件..."
    cp .env.example .env
    echo "请根据需要修改.env文件中的配置"
fi

# 创建数据库目录
if [ ! -d database ]; then
    echo "创建数据库目录..."
    mkdir -p database
fi

echo "部署完成！"
echo "使用以下命令启动服务:"
echo "  npm start"
echo "服务默认运行在 http://localhost:3000"