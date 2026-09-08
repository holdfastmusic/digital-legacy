#!/bin/bash
# Installa/aggiorna l'alias claude-brain in ~/.zshrc
# Esegui con: bash scripts/fix-local-alias.sh

VAULT="$HOME/Documents/VaultFrancesco"
ZSHRC="$HOME/.zshrc"
ALIAS_LINE="alias claude-brain='cd ~/Documents/VaultFrancesco && (npx obsidian-mcp ~/Documents/VaultFrancesco > /dev/null 2>&1 &) && claude'"

echo "=== fix-local-alias.sh ==="

# 1. Verifica che il vault esista
if [ ! -d "$VAULT" ]; then
  echo "ATTENZIONE: $VAULT non esiste."
  echo "Crea la directory e assicurati che CLAUDE.md sia presente:"
  echo "  mkdir -p $VAULT"
  echo "  cp $(dirname "$0")/../CLAUDE.md $VAULT/CLAUDE.md"
fi

# 2. Rimuovi eventuali versioni precedenti dell'alias
if grep -q 'claude-brain' "$ZSHRC" 2>/dev/null; then
  echo "Rimozione alias claude-brain esistente da $ZSHRC..."
  sed -i.bak '/claude-brain/d' "$ZSHRC"
fi

# 3. Aggiungi l'alias aggiornato
echo "" >> "$ZSHRC"
echo "# Claude Brain — avvia Claude Code nel vault Obsidian" >> "$ZSHRC"
echo "$ALIAS_LINE" >> "$ZSHRC"
echo "Alias aggiunto a $ZSHRC"

# 4. Verifica CLAUDE.md nel vault
if [ -d "$VAULT" ] && [ ! -f "$VAULT/CLAUDE.md" ]; then
  echo "CLAUDE.md non trovato nel vault. Copia dal repo:"
  SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
  REPO_CLAUDE="$SCRIPT_DIR/../CLAUDE.md"
  if [ -f "$REPO_CLAUDE" ]; then
    cp "$REPO_CLAUDE" "$VAULT/CLAUDE.md"
    echo "Copiato $REPO_CLAUDE → $VAULT/CLAUDE.md"
  fi
fi

# 5. Verifica dipendenze
echo ""
echo "=== Verifica dipendenze ==="
command -v claude >/dev/null 2>&1 && echo "✓ claude CLI trovato" || echo "✗ claude CLI non trovato — installa con: npm install -g @anthropic-ai/claude-code"
command -v npx >/dev/null 2>&1 && echo "✓ npx trovato" || echo "✗ npx non trovato — installa Node.js"

echo ""
echo "=== Test finale ==="
echo "Esegui: source ~/.zshrc && claude-brain"
echo "La prima risposta di Claude dovrebbe includere il contesto da CLAUDE.md"
