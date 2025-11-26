@echo off

REM 智能投资助手后端部署脚本（Windows版）
echo 开始部署智能投资助手后端...

REM 检查Node.js环境
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo 错误: 未找到Node.js。请先安装Node.js 16+
    exit /b 1
)

REM 检查npm环境
where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo 错误: 未找到npm。请先安装npm 7+
    exit /b 1
)

echo Node.js版本: 
node -v
echo npm版本: 
npm -v

REM 安装依赖
echo 正在安装依赖...
npm install --production

if %errorlevel% neq 0 (
    echo 错误: 依赖安装失败
    exit /b 1
)

REM 创建环境变量文件
if not exist .env (
    echo 创建.env配置文件...
    copy .env.example .env
    echo 请根据需要修改.env文件中的配置
)

REM 创建数据库目录
if not exist database (
    echo 创建数据库目录...
    mkdir database
)

echo 部署完成！
echo 使用以下命令启动服务:
echo   npm start
echo 服务默认运行在 http://localhost:3000