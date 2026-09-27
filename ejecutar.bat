@echo off
setlocal
title ConciliaChain
echo Iniciando ConciliaChain...
python arranque.py
if errorlevel 1 (
  echo.
  echo No se pudo iniciar ConciliaChain. Instala Python 3.10 o superior.
  pause
)
