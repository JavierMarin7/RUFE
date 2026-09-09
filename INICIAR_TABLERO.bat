@echo off
chcp 65001 >nul
title Tablero RUFE - Valle del Cauca
cd /d "%~dp0"

echo.
echo   Afectacion por sismo - Registros RUFE / Valle del Cauca
echo   -------------------------------------------------------
echo.

set "PY="

rem 1) lanzador oficial de Windows
py -3 --version >nul 2>nul && set "PY=py -3"

rem 2) python en el PATH
if not defined PY (
  python --version >nul 2>nul && set "PY=python"
)
if not defined PY (
  python3 --version >nul 2>nul && set "PY=python3"
)

rem 3) entorno conda activo en esta sesion
if not defined PY if defined CONDA_PREFIX (
  if exist "%CONDA_PREFIX%\python.exe" set "PY=%CONDA_PREFIX%\python.exe"
)

rem 4) instalaciones tipicas de Anaconda / Miniconda
if not defined PY (
  for %%D in (
    "%USERPROFILE%\anaconda3"
    "%USERPROFILE%\miniconda3"
    "%USERPROFILE%\AppData\Local\Programs\Python\Python312"
    "%USERPROFILE%\AppData\Local\Programs\Python\Python311"
    "%LOCALAPPDATA%\Programs\Python\Python310"
    "C:\ProgramData\anaconda3"
  ) do (
    if not defined PY if exist "%%~D\python.exe" set "PY=%%~D\python.exe"
  )
)

if defined PY (
  echo   Servidor local en http://localhost:8000
  echo   Deja esta ventana abierta mientras uses el tablero.
  echo.
  start "" http://localhost:8000/index.html
  %PY% -m http.server 8000
  goto :eof
)

echo   No se encontro Python. Se usara el servidor de PowerShell,
echo   que viene incluido en Windows.
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\servidor.ps1"
if errorlevel 1 (
  echo.
  echo   Si tampoco funciono, abre ABRIR_SIN_SERVIDOR.html con doble clic.
  echo.
  pause
)
