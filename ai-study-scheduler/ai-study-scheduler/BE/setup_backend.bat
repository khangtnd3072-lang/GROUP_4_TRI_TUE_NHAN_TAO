@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ===============================================
echo   CAI DAT BACKEND - AI STUDY SCHEDULER
ECHO ===============================================
echo.
where py >nul 2>nul
if %errorlevel%==0 (
    set PYTHON_CMD=py
) else (
    set PYTHON_CMD=python
)

if not exist ".venv\Scripts\python.exe" (
    echo [1/4] Tao moi truong ao .venv...
    %PYTHON_CMD% -m venv .venv
    if errorlevel 1 goto :error
) else (
    echo [1/4] .venv da ton tai - bo qua.
)

echo [2/4] Nang cap pip...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto :error

echo [3/4] Cai dependencies...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto :error

if not exist ".env" (
    echo [4/4] Tao .env tu .env.example...
    copy /Y ".env.example" ".env" >nul
) else (
    echo [4/4] .env da ton tai - giu nguyen.
)

echo.
echo ===============================================
echo Cai dat Backend thanh cong.
echo Tiep theo: Start MySQL XAMPP, import database,
echo sau do chay run_backend.bat.
echo ===============================================
pause
exit /b 0

:error
echo.
echo [LOI] Cai dat that bai. Kiem tra Python va ket noi Internet.
pause
exit /b 1
