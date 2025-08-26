@echo off
rem Set console encoding to UTF-8 for better character display
chcp 65001 > nul

rem Check if the virtual environment exists
IF NOT EXIST ".\.venv\Scripts\python.exe" (
    echo Error: Virtual environment not found at ".\.venv\Scripts\python.exe".
    echo Please ensure the .venv is created and activated, or check its path.
    goto :end
)

rem Start the game using the virtual environment's Python interpreter
echo Starting the LingCard game...
echo.

".\.venv\Scripts\python.exe" ".\main.py"

rem Pause to keep the console window open after the script finishes
echo.
echo Game finished. Press any key to exit.
pause > nul

:end