@echo off

:: Ruta al entorno virtual
set VIRTUAL_ENV_DIR=C:\Users\anton\docs\04. ES3\screen-action-logger\env

:: Activa el entorno virtual
call "%VIRTUAL_ENV_DIR%\Scripts\activate"

:: Ejecuta el script Python
python "%VIRTUAL_ENV_DIR%\..\main.py"

:: Desactiva el entorno virtual (opcional)
deactivate
