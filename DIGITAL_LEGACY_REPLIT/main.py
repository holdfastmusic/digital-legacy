# File principale per Replit
# Questo file avvia Digital Legacy

import os
import sys

# Aggiungi il percorso src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Importa e avvia l'app
from src.main import app

if __name__ == "__main__":
    # Replit usa la porta dalla variabile d'ambiente
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

