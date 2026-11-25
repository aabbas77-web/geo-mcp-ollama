@echo off
setlocal

REM --- Always run from the folder this .bat lives in ---
cd /d "%~dp0"

echo ============================================
echo   Geo MCP Ollama - Environment Setup
echo   Working directory: %CD%
echo ============================================

REM 1. Verify Python is available
python --version >nul 2>nul
if errorlevel 1 goto :no_python

REM 2. Create the venv if it does not exist
if not exist ".venv" goto :create_venv
echo [1/4] Virtual environment already exists.
goto :activate_venv

:create_venv
echo [1/4] Creating virtual environment in .venv ...
python -m venv .venv
if errorlevel 1 goto :venv_failed

:activate_venv
echo [2/4] Activating virtual environment ...
call .venv\Scripts\activate.bat

REM 3. Verify pip inside the venv; repair if missing
echo [3/4] Verifying pip in the virtual environment ...
python -m pip --version >nul 2>nul
if not errorlevel 1 goto :pip_ok

echo    pip is missing - attempting repair with ensurepip ...
python -m ensurepip --upgrade
python -m pip --version >nul 2>nul
if not errorlevel 1 goto :pip_restored

echo    ensurepip failed - recreating the virtual environment ...
rmdir /s /q .venv
python -m venv .venv
call .venv\Scripts\activate.bat
python -m ensurepip --upgrade
python -m pip --version >nul 2>nul
if not errorlevel 1 goto :pip_restored

echo [ERROR] Could not restore pip even after recreating the venv.
echo         Please repair your Python installation (Settings - Apps - Python - Modify - Repair).
pause
exit /b 1

:pip_restored
echo    pip has been restored.
goto :install

:pip_ok
echo    pip is already available.

:install
REM 4. Upgrade pip and install requirements
echo [4/4] Installing dependencies from requirements.txt ...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 goto :pip_install_failed

echo.
echo ============================================
echo   Setup complete!
echo   Run 02_start_ollama.bat to launch Ollama LLMs.
echo   Run 03_start_ai_geo_server_ollama_client.bat to launch AI GeoServer Client.
echo ============================================
pause
endlocal
exit /b 0

:no_python
echo [ERROR] Python not found on PATH. Install Python 3.10+ first.
pause
exit /b 1

:venv_failed
echo [ERROR] Failed to create virtual environment.
pause
exit /b 1

:pip_install_failed
echo [ERROR] pip install failed.
pause
exit /b 1