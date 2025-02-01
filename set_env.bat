@echo off
REM This is Windows equivalent to source .env
FOR /F "eol=# tokens=*" %%i IN (%~dp0.env) DO set %%i
