@echo off
title Sistema de Correos - Detener Todo
color 0C

echo ============================================
echo   Deteniendo todos los servicios
echo ============================================
echo.

echo [INFO] Deteniendo procesos de Python (Backend)...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Backend*" 2>nul
taskkill /F /FI "WINDOWTITLE eq Backend - Puerto 7373*" 2>nul

echo [INFO] Deteniendo procesos de Node.js (Frontend)...
taskkill /F /IM node.exe /FI "WINDOWTITLE eq Frontend*" 2>nul
taskkill /F /FI "WINDOWTITLE eq Frontend - Puerto 7171*" 2>nul

echo [INFO] Liberando puertos...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :7373 ^| findstr LISTENING') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :7171 ^| findstr LISTENING') do taskkill /F /PID %%a 2>nul

echo.
echo ============================================
echo   Todos los servicios han sido detenidos
echo ============================================
echo.
pause