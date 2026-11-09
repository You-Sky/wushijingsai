@echo off
chcp 65001 >nul
cd /d "%~dp0"
if exist "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe" set "PATH=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin;%PATH%"
where node >nul 2>nul
if errorlevel 1 (
  echo 请先安装 Node.js 22 或更新版本，再双击此文件。
  pause
  exit /b 1
)
if not exist "dist\index.html" (
  echo 缺少构建文件。请按 README.md 运行 pnpm install 和 pnpm build。
  pause
  exit /b 1
)
node scripts\serve.mjs --open
pause
