@echo off

REM 设置颜色
echo 设置控制台颜色...
color 0A

REM 显示欢迎信息
echo. 
echo ==============================================================
echo                      投资助手系统启动脚本
 echo ==============================================================
echo. 

REM 检查Node.js环境
echo 检查Node.js环境...
node -v >nul 2>nul
if %errorlevel% neq 0 (
    echo 错误: 未找到Node.js环境，请先安装Node.js
    pause
    exit /b 1
)
echo Node.js环境正常

REM 创建日志文件夹
mkdir logs >nul 2>nul

REM 启动后端服务
echo. 
echo 启动后端服务...
start "后端服务" cmd /k "cd backend && npm install >nul 2>nul && npm start > ../logs/backend.log 2>&1"

REM 等待后端服务启动（3秒）
echo 等待后端服务初始化...
ping 127.0.0.1 -n 4 >nul

REM 启动前端服务
echo. 
echo 启动前端服务...
start "前端服务" cmd /k "npm install >nul 2>nul && npm run dev"

REM 等待前端服务启动（5秒）
echo 等待前端服务初始化...
ping 127.0.0.1 -n 6 >nul

REM 自动打开浏览器
echo. 
echo 正在打开浏览器...
start http://localhost:5173

echo. 
echo ==============================================================
echo 系统启动完成！正在自动打开浏览器...
echo 如果浏览器未自动打开，请手动访问 http://localhost:5173
echo 如需查看后端日志，请查看 logs/backend.log 文件
echo ==============================================================
echo. 
echo 按任意键继续...
pause >nul
