@echo off
chcp 65001 >nul
title 精益SOP助手 - 启动器

:: 设置窗口颜色
color 0A

:: 切换到脚本所在目录
cd /d "%~dp0"

cls
echo ╔══════════════════════════════════════════╗
echo ║      精益SOP智能助手 - 一键启动器        ║
echo ╚══════════════════════════════════════════╝
echo.
echo [1/4] 检查 Python 环境...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [失败] 未找到 Python，请先安装 Python
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version 2^>^&1') do echo        Python 版本: %%i

echo.
echo [2/4] 检查 Streamlit...
python -c "import streamlit" >nul 2>&1
if %errorlevel% neq 0 (
    echo [失败] 未安装 Streamlit，正在安装依赖...
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    if %errorlevel% neq 0 (
        echo [错误] 依赖安装失败！
        pause
        exit /b 1
    )
    echo [完成] 依赖安装成功
) else (
    echo       Streamlit 已就绪
)

echo.
echo [3/4] 检查知识库...
if not exist "knowledge_base\chunks.pkl" (
    echo [提示] 知识库未构建，正在构建...
    echo        首次构建需下载模型文件（约 300MB）
    python build_knowledge_base.py
    if %errorlevel% neq 0 (
        echo [错误] 知识库构建失败
        pause
        exit /b 1
    )
    echo [完成] 知识库构建成功
) else (
    echo       知识库已就绪
)

echo.
echo [4/4] 启动精益SOP助手...
echo.
echo    ▸ 启动服务后浏览器将自动打开
echo    ▸ 访问地址: http://localhost:8501
echo    ▸ 关闭此窗口即可停止服务
echo    ▸ 按 Ctrl+C 可中断服务
echo.
echo ============================================
echo         正在启动，请稍候...
echo ============================================
echo.

:: 启动 Streamlit 并自动打开浏览器
start http://localhost:8501
python -m streamlit run sop_assistant.py

echo.
echo 服务已停止。
pause
