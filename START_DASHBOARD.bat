@echo off
setlocal
cd /d "%~dp0"
set "CASE_PYTHON=%~dp0..\..\..\.venv\Scripts\python.exe"
if not exist "%CASE_PYTHON%" (
    echo Python is niet gevonden. Laat deze startknop in de map dashboard staan.
    pause
    exit /b 1
)
echo Het dashboard wordt gestart. Je browser opent vanzelf.
echo Laat dit venster open zolang je het dashboard gebruikt.
echo Stoppen kan met Ctrl+C.
echo.
"%CASE_PYTHON%" -m streamlit run "%~dp0app.py" --server.headless=false
if errorlevel 1 pause
