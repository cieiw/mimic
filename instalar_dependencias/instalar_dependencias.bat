@echo off
setlocal
title Instalar dependencias - Mimic

cd /d "%~dp0"

echo.
echo ========================================
echo   Instalando dependencias do Mimic
echo ========================================
echo.

set "PY_CMD="
where py >nul 2>nul
if not errorlevel 1 set "PY_CMD=py -3"

if not defined PY_CMD (
    where python >nul 2>nul
    if not errorlevel 1 set "PY_CMD=python"
)

if not defined PY_CMD (
    echo Python nao encontrado no PATH.
    echo Instale o Python 3 e marque a opcao "Add python.exe to PATH".
    echo.
    pause
    exit /b 1
)

echo Python:
%PY_CMD% --version
echo.

echo Atualizando pip...
%PY_CMD% -m pip install --upgrade pip
if errorlevel 1 goto erro

echo.
echo Instalando bibliotecas Python...
%PY_CMD% -m pip install -r "%~dp0requirements.txt"
if errorlevel 1 goto erro

echo.
echo Instalando navegador do Playwright...
%PY_CMD% -m playwright install chromium
if errorlevel 1 goto erro

echo.
echo Verificando FFmpeg...
where ffmpeg >nul 2>nul
if errorlevel 1 (
    echo FFmpeg nao encontrado no PATH.
    where winget >nul 2>nul
    if errorlevel 1 (
        echo Winget nao encontrado. Instale o FFmpeg manualmente se for usar videos.
    ) else (
        echo Tentando instalar FFmpeg pelo winget...
        winget install --id Gyan.FFmpeg -e --accept-package-agreements --accept-source-agreements
        echo Se o ffmpeg ainda nao aparecer no PATH, feche e abra o terminal/Windows.
    )
) else (
    echo FFmpeg ja encontrado.
)

echo.
echo Dependencias instaladas.
pause
exit /b 0

:erro
echo.
echo Falha ao instalar dependencias.
pause
exit /b 1
