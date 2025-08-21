@echo off
@REM Check if WSL is installed
where wsl >nul 2>nul
if %errorlevel% neq 0 (
    echo WSL is not installed on this system.
    echo Please install Windows Subsystem for Linux (WSL) first.
    echo You can install it by running: wsl --install
    pause
    exit /b 1
)

@REM Run build_and_deploy.sh inside WSL
echo Running build_and_deploy.sh in WSL...
wsl bash -c "sed -i 's/\r$//' build_and_deploy.sh && ./build_and_deploy.sh"

@REM Check exit code
if %errorlevel% neq 0 (
    echo The build_and_deploy.sh script failed.
    pause
    exit /b 1
)

echo Build and deploy completed successfully.
pause
