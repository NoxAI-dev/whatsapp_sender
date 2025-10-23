@echo off
title Builder - WhatsApp Sender (Nox)
color 0A
setlocal

echo.
echo ===============================================
echo   AMBIENTE DE BUILD - WHATSAPP SENDER
echo   by NoxAI
echo ===============================================
echo.

REM 1) venv
if not exist .venv (
  echo [1/4] Criando venv...
  python -m venv .venv
)

REM 2) ativar venv
echo [2/4] Ativando venv...
call .venv\Scripts\activate

REM 3) deps
echo [3/4] Instalando dependencias...
pip install --upgrade pip >nul
pip install -r requirements-win.txt

REM 4) build (usa SEU arquivo: send_whatsapp.py)
echo [4/4] Gerando executavel (onedir)...
pyinstaller --onedir --name whatsapp_sender --clean send_whatsapp.py

echo.
echo ===== BUILD CONCLUIDO =====
echo EXE: dist\whatsapp_sender\whatsapp_sender.exe
echo ============================
echo.
pause
