@echo off
setlocal

REM --- Always run from the folder this .bat lives in ---
cd /d "%~dp0"

echo ============================================
echo   Geo MCP Ollama - Starting Client + Server
echo   Working directory: %CD%
echo ============================================
echo.

REM 1. Ensure the virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found in:
    echo         %CD%\.venv
    echo Please run 01_setup.bat first.
    echo.
    pause
    exit /b 1
)

REM 2. Ensure the required Python files are present
if not exist "ollama_client.py" (
    echo [ERROR] ollama_client.py not found in %CD%
    echo.
    pause
    exit /b 1
)
if not exist "geo_server.py" (
    echo [ERROR] geo_server.py not found in %CD%
    echo.
    pause
    exit /b 1
)

REM 3. Activate the venv
call .venv\Scripts\activate.bat

REM --- FIX: Bypass system proxy for local Ollama calls ---
set NO_PROXY=localhost,127.0.0.1,::1

REM --- Optional: uncomment if Ollama crashes on GPU (0xc0000005) ---
REM set OLLAMA_LLM_LIBRARY=cpu

REM 4. Launch the MCP client (spawns the GIS server via stdio)
python ollama_client.py geo_server.py

echo.
echo ============================================
echo   Finished. Press any key to close.
echo ============================================
pause
endlocal