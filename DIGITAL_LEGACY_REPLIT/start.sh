#!/bin/bash

echo "🚀 Avvio Digital Legacy MVP..."
echo ""

# Controlla se siamo nella directory corretta
if [ ! -f "src/main.py" ]; then
    echo "❌ Errore: Esegui questo script dalla cartella digital_legacy_backend"
    exit 1
fi

# Attiva ambiente virtuale
echo "📦 Attivazione ambiente virtuale..."
source venv/bin/activate

# Controlla dipendenze
echo "🔍 Controllo dipendenze..."
if ! pip list | grep -q Flask; then
    echo "📥 Installazione dipendenze..."
    pip install -r requirements.txt
fi

# Avvia applicazione
echo ""
echo "🎉 Digital Legacy è pronto!"
echo "📱 Apri il browser su: http://localhost:5000"
echo "🌐 Per condividere usa ngrok: ngrok http 5000"
echo ""
echo "⏹️  Premi Ctrl+C per fermare"
echo ""

python src/main.py

