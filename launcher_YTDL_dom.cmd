@echo off
@color 71


REM cd %~dp0
CALL "%~dp0venvd\Scripts\activate.bat"
start /B /D "%~dp0venvd\Scripts" "python.exe" "%~dp0YouTubeDl_GUI.py"
REM start /B "" "%~dp0venvd\Scripts\python.exe" "%~dp0YouTubeDl_GUI.py"
REM pause
