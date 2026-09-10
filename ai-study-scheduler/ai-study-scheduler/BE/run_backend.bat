@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ===============================================
echo   AI STUDY SCHEDULER - BACKEND
ECHO   Python FastAPI + MySQL/XAMPP
ECHO ===============================================
echo.
if not exist ".venv\Scripts\python.exe" (
    echo [LOI] Chua tim thay moi truong ao BE\.venv
    echo Hay doc file HUONG_DAN_CHAY_CHUONG_TRINH.md va cai dependency truoc.
    echo.
    pause
    exit /b 1
)
if not exist ".env" (
    echo [CANH BAO] Chua co file BE\.env
    echo Dang tao .env tu .env.example voi cau hinh XAMPP mac dinh...
    copy /Y ".env.example" ".env" >nul
)
echo Backend se chay tai: http://127.0.0.1:8000
ECHO API docs: http://127.0.0.1:8000/docs
ECHO Nhan Ctrl+C de dung server.
echo.
".venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
pause
