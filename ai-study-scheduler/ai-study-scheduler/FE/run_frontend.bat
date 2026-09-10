@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ===============================================
echo   AI STUDY SCHEDULER - FRONTEND
ECHO   HTML / CSS / JavaScript
ECHO ===============================================
echo.
echo Frontend se chay tai: http://127.0.0.1:5500
ECHO Nhan Ctrl+C de dung server.
echo.
where py >nul 2>nul
if %errorlevel%==0 (
    py -m http.server 5500 --bind 127.0.0.1
) else (
    python -m http.server 5500 --bind 127.0.0.1
)
pause
