@echo off
title Instalando y ejecutando Tetris
cls
echo.
echo  ╔════════════════════════════════════════════════════════════╗
echo  ║                    TETRIS GAME                             ║
echo  ║                                                            ║
echo  ║           HECHO POR:                                       ║
echo  ║           - Melanie Tomala                                 ║
echo  ║           - Jean Cedeño                                    ║
echo  ║           - Damian Torres                                  ║
echo  ╚════════════════════════════════════════════════════════════╝
echo.
pause
echo =========================================
echo     Verificando si Python está instalado
echo =========================================
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo Python no está instalado.
    echo Descargando instalador de Python...
    curl https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe -o python_installer.exe
    echo Instalando Python...
    start /wait python_installer.exe /quiet InstallAllUsers=1 PrependPath=1
    del python_installer.exe
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
python cascara_tetris.py
pause
