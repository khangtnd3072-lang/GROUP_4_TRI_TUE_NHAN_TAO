@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Dang mo Backend va Frontend...
start "AI Study Scheduler - Backend" cmd /k call "%~dp0BE\run_backend.bat"
timeout /t 2 /nobreak >nul
start "AI Study Scheduler - Frontend" cmd /k call "%~dp0FE\run_frontend.bat"
echo.
echo Sau khi hai server khoi dong, mo:
echo http://127.0.0.1:5500
echo.
pause
