@echo off
REM Script para obtener token JWT del backend UrbanVibe

echo ======================================================================
echo OBTENIENDO TOKEN DE AUTENTICACION
echo ======================================================================
echo.

set API_URL=http://localhost:8000
set EMAIL=local@urbanvibe.cl
set PASSWORD=password123

echo Endpoint: %API_URL%/api/v1/auth/login
echo Email: %EMAIL%
echo.

REM Hacer request de login
curl -X POST "%API_URL%/api/v1/auth/login" ^
     -H "Content-Type: application/json" ^
     -d "{\"email\":\"%EMAIL%\",\"password\":\"%PASSWORD%\"}" ^
     -o response.json

echo.
echo ======================================================================
echo RESPUESTA:
echo ======================================================================
type response.json
echo.
echo ======================================================================

REM Extraer token (requiere jq o procesamiento manual)
echo.
echo Para extraer el token, abre response.json y copia el valor de "access_token"
echo.

pause
