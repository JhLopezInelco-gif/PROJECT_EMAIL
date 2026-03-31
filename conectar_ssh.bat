@echo off
setlocal PASSWORD=%1
setlocal IP=187.124.224.233
setlocal PORT=22
setlocal USER=root
setlocal KEYFILE=C:\Users\jhlopez\.ssh\id_ed25519

setlocal COMMAND=%2

echo ============================================
echo Intentando conectar a %IP%:%PORT% como %USER%
echo ============================================
echo.

:retry
ssh -o StrictHostKeyChecking=no -o ConnectTimeout=30 -p %PORT% -i %KEYFILE% %USER%@%IP% "%COMMAND%"
if %ERRORLEVEL% EQU 0 (
    echo Conexion exitosa!
    goto :success
) else (
    echo Error: %ERRORLEVEL%
    goto :retry
)

:success
echo Presione cualquier tecla para abrir una sesion interactiva...
pause