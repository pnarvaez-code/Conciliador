@echo off
setlocal
title ConciliaChain - Web
echo Iniciando ConciliaChain web...
start "" /b python -m http.server 8000 --directory docs
timeout /t 2 /nobreak >nul
start "" http://127.0.0.1:8000
if errorlevel 1 (
  echo.
  echo No se encontro Python. Puedes abrir docs\index.html directamente.
  pause
)
