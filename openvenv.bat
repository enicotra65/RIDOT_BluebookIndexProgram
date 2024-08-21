@echo off

:: Path to your virtual environment
set VENV_PATH=C:\Users\evans\PycharmProjects\RIDOT_BluebookIndexProgram\venv

:: Activate the virtual environment
call %VENV_PATH%\Scripts\activate.bat

:: Run your Flask application
python app.py
