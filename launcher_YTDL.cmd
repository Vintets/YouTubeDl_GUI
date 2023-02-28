@echo off
@color 71

REM cd %~dp0
start /B /D "%~dp0venv\Scripts" "python.exe" "%~dp0YouTubeDl_GUI.py"
REM start /B "" "%~dp0venv\Scripts\python.exe" "%~dp0YouTubeDl_GUI.py"
REM pause
