@echo off
title Digital Legacy MVP

echo 🚀 Avvio Digital Legacy MVP...
echo.

REM Controlla se siamo nella directory corretta
if not exist "src\main.py" (
    echo ❌ Errore: Esegui questo script dalla cartella digital_legacy_backend
    pause
    exit /b 1
)

REM Attiva ambiente virtuale
echo 📦 Attivazione ambiente virtuale...
call venv\Scripts\activate

REM Controlla dipendenze
echo 🔍 Controllo dipendenze...
pip list | findstr Flask >nul
if errorlevel 1 (
    echo 📥 Installazione dipendenze...
    pip install -r requirements.txt
)

REM Avvia applicazione
echo.
echo 🎉 Digital Legacy è pronto!
echo 📱 Apri il browser su: http://localhost:5000
echo 🌐 Per condividere usa ngrok: ngrok http 5000
echo.
echo ⏹️  Premi Ctrl+C per fermare
echo.

python src\main.py

pause

