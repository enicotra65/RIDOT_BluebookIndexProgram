@echo off

:: Dynamically find the virtual environment directory
setlocal enabledelayedexpansion

set "VENV_DIR="
for /d %%D in ("%~dp0\*") do (
    if exist "%%D\Scripts\activate.bat" (
        set "VENV_DIR=%%D"
        goto :found
    )
)

:found
if not defined VENV_DIR (
    echo Virtual environment not found.
    exit /b 1
)

:: Activate the virtual environment
call "%VENV_DIR%\Scripts\activate.bat"

:: Run the Flask application
python app.py
