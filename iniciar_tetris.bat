@echo off
title Instalando y ejecutando Tetris
echo =========================================
echo       Verificando si Python esta instalado
echo =========================================

:: Verificacion de Python
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo Python no esta instalado.
    echo Descargando instalador de Python...

    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile 'python_installer.exe'"

    echo Instalando Python...
    :: Se instala y se intenta actualizar el PATH
    start /wait python_installer.exe /quiet InstallAllUsers=1 PrependPath=1
    del python_installer.exe

    echo.
    echo Python instalado correctamente.
    echo NOTA: Si el script falla despues de esto, cierra y vuelve a abrirlo para recargar las variables de entorno.
) ELSE (
    echo Python ya esta instalado.
)

echo.
echo =========================================
echo        Instalando dependencias
echo =========================================

:: Verificamos si existe el script de dependencias
IF EXIST "instalar_dependencias.py" (
    python instalar_dependencias.py
) ELSE (
    echo [ADVERTENCIA] No se encontro 'instalar_dependencias.py'. Saltando paso.
)

echo.
echo =========================================
echo           Ejecutando Tetris
echo =========================================

:: Verificamos si la carpeta src existe antes de entrar
IF EXIST "src" (
    cd src
    python cascara_tetris.py
) ELSE (
    echo [ERROR] La carpeta 'src' no existe. Asegurate de estar en el directorio correcto.
)

echo.
echo =========================================
echo    Proceso finalizado. Todo descargado.
echo =========================================
pause
