@echo off
chcp 65001 >nul
title Validacion del paquete RUFE
cd /d "%~dp0"

set "PY="
py -3 --version >nul 2>nul && set "PY=py -3"
if not defined PY ( python --version >nul 2>nul && set "PY=python" )
if not defined PY if defined CONDA_PREFIX (
  if exist "%CONDA_PREFIX%\python.exe" set "PY=%CONDA_PREFIX%\python.exe"
)
if not defined PY (
  for %%D in ("%USERPROFILE%\anaconda3" "%USERPROFILE%\miniconda3" "C:\ProgramData\anaconda3") do (
    if not defined PY if exist "%%~D\python.exe" set "PY=%%~D\python.exe"
  )
)

if not defined PY (
  echo.
  echo   La validacion necesita Python y no se encontro ninguno.
  echo   El tablero si funciona sin Python: usa INICIAR_TABLERO.bat.
  echo.
  pause
  exit /b 1
)

%PY% scripts\validar_paquete.py
echo.
pause
