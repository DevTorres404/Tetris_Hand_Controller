@echo off
title Instalando y ejecutando Tetris
echo =========================================
echo     Verificando si Python está instalado
echo =========================================

python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo Python no está instalado.
    echo Descargando instalador de Python...

    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile 'python_installer.exe'"

    echo Instalando Python...
    start /wait python_installer.exe /quiet InstallAllUsers=1 PrependPath=1
    del python_installer.exe

    echo.
    echo Python instalado correctamente.
) ELSE (
    echo Python ya está instalado.
)

echo.
echo =========================================
echo       Instalando dependencias
echo =========================================
python instalar_dependencias.py

echo.
echo =========================================
echo         Ejecutando Tetris
echo =========================================

REM Entrar a la carpeta src
cd src

python cascara_tetris.py

pause
