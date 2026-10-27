@echo off
title VoiceForge - Installation Wizard
color 17
echo.
echo ================================================================
echo VoiceForge - AI Text-to-Speech Studio
echo ================================================================
echo.
python --version >nul 2>&1
if %errorlevel% neq 0 (
  echo Python was not found. Install Python 3.11 or newer, then retry.
  echo Download: https://www.python.org/downloads/windows/
  pause
  exit /b 1
)
if not exist runtime mkdir runtime
if not exist runtime\venv python -m venv runtime\venv
if %errorlevel% neq 0 (
  echo Failed to create the virtual environment.
  pause
  exit /b 1
)
runtime\venv\Scripts\python.exe -m pip install --upgrade pip
runtime\venv\Scripts\python.exe -m pip install -r requirements.txt
if %errorlevel% neq 0 (
  echo Dependency installation failed. Check Python compatibility and internet access.
  pause
  exit /b 1
)
if not exist data\bgm mkdir data\bgm
if not exist data\cloned mkdir data\cloned
if not exist logs mkdir logs
if not exist output mkdir output
echo.
echo Setup complete. You can run VoiceForge.vbs to launch.
pause
start "" wscript.exe "VoiceForge.vbs"
