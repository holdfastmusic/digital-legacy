# VPS Setup per sessioni Claude Code sempre-on

Obiettivo: accedere e far lavorare agenti Claude anche quando il Mac è spento.

## Opzione A — Claude Code on the Web (già attivo, zero setup)

Il modo più semplice. Tutte le sessioni su `claude.ai/code` girano già su server Anthropic.
Il repo `digital-legacy` è connesso: basta aprire una sessione web e il contesto è nel `CLAUDE.md` del repo.

**Limitazione**: ogni sessione è un container effimero. Non ha accesso diretto al server Dell.

## Opzione B — Claude Code CLI su VPS/server Dell

Installa Claude Code CLI sul server Dell (già in esecuzione su holdfastmusic.it).

```bash
# Sul server Dell (SSH)
npm install -g @anthropic-ai/claude-code

# Imposta API key
export ANTHROPIC_API_KEY="sk-ant-..."
echo 'export ANTHROPIC_API_KEY="sk-ant-..."' >> ~/.bashrc

# Alias brain (senza obsidian-mcp se il vault non è sul server)
echo "alias claude-brain='cd ~/VaultFrancesco && claude'" >> ~/.bashrc
source ~/.bashrc
```

Poi usa `claude-brain` via SSH dal Mac o da qualsiasi device.

**Pro**: accesso diretto ai servizi locali (Kujan :3000, n8n :5678, ecc.)  
**Contro**: gestione sessioni SSH, nessuna UI

## Opzione C — tmux + SSH (sessioni persistenti)

```bash
# Sul server Dell
tmux new -s brain
claude-brain

# Detach: Ctrl+B, D
# Reconnect da qualsiasi device:
ssh user@holdfastmusic.it -t "tmux attach -t brain"
```

Questo mantiene la sessione Claude attiva anche quando disconnetti.

## Opzione D — VPS dedicata (Hetzner/DigitalOcean)

Se vuoi separare i workload dal server Dell:

- **Hetzner CX22**: 2 vCPU, 4GB RAM, ~4€/mese
- Installa Node.js + Claude Code CLI
- Clona il repo `digital-legacy`
- Configura `.claude/settings.json` con i permessi necessari

```bash
# Provisioning rapido
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs git
npm install -g @anthropic-ai/claude-code
git clone https://github.com/holdfastmusic/digital-legacy ~/digital-legacy
cd ~/digital-legacy && claude
```

## Raccomandazione

Per il tuo caso (server Dell sempre acceso + Mac usato da mobile):

→ **Opzione B + C**: installa Claude Code CLI sul Dell con tmux.  
Accedi via SSH da iPad/iPhone usando un'app come Blink o Termius.  
Costo: €0 (usi hardware già esistente).

Se vuoi UI grafica senza SSH → resta su **Claude.ai/code** (Opzione A).
