@echo off
REM Activate virtual environment for interactive use
REM Run this to activate .venv in your current shell

set ROOT=%~dp0

echo Activating virtual environment...
echo.

if exist "%ROOT%\.venv\Scripts\activate.bat" (
    call "%ROOT%\.venv\Scripts\activate.bat"
    echo Virtual environment activated!
    echo Working directory: %ROOT%
    echo.
    echo You are now in the activated virtual environment.
    echo Type 'deactivate' to exit the virtual environment.
    echo.
    cd /d "%ROOT%"
) else (
    echo WARNING: No .venv found at %ROOT%\.venv
    echo Create a virtual environment with: python -m venv .venv
    echo.
    pause
    exit /b 1
)
