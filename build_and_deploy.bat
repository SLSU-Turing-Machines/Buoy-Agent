@echo off
echo 📦 Building Svelte frontend...
cd svelte
npm run build
cd ..

echo 📁 Syncing Svelte build to src\buoy-ai-frontend\assets\...
rmdir /s /q src\buoy-ai-frontend\assets\
mkdir src\buoy-ai-frontend\assets
xcopy /s /e /y svelte\build\* src\buoy-ai-frontend\assets\

echo 🚀 Deploying to Internet Computer...
dfx deploy

echo 🐍 Starting Flask server...
cd app

if exist .venv\Scripts\activate (
    call .venv\Scripts\activate
) else (
    echo Virtual environment not found, running without it.
)

python app.py
