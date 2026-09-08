# Digital Legacy — Contesto Claude Code

## Progetto attivo: digital-legacy
App Flask per la gestione del patrimonio digitale (lascito): asset digitali, beneficiari, piani di successione.

### Stack
- **Backend**: Python/Flask + SQLAlchemy + SQLite (`DIGITAL_LEGACY_REPLIT/`)
- **Frontend**: SPA React precompilata in `static/`
- **Avvio locale**: `python main.py` (porta 5000)

### File chiave
- `DIGITAL_LEGACY_REPLIT/src/main.py` — entry point Flask, registrazione blueprint
- `DIGITAL_LEGACY_REPLIT/src/models/` — User, DigitalAsset, Beneficiary, AssetAssignment, SuccessionPlan
- `DIGITAL_LEGACY_REPLIT/src/routes/` — API REST per ogni modello
- `DIGITAL_LEGACY_REPLIT/src/database/app.db` — SQLite DB

---

## Ecosistema holdfastmusic.it (VPS Hetzner)

**VPS**: Hetzner CPX22 — 178.105.178.10 — Ubuntu 22.04 — Nuremberg
**SSH**: `ssh holdfast-vps` (alias in ~/.ssh/config, user root, chiave ~/.ssh/id_ed25519_reelforge)
**Nota**: il Dell di casa (192.168.1.46) è DISMESSO come server principale (RAM difettosa) — usato solo come backup LAN. Lo script `deploy.sh` di CFO-AI punta ancora al vecchio IP — da aggiornare.

| Servizio | URL | Porta |
|---|---|---|
| Kujan (CRM) | kujan.holdfastmusic.it | 3000 |
| Kinsu | kinsu.eu / kinsu.holdfastmusic.it | 8766 |
| CFO.ai | cfo.holdfastmusic.it | 8502 |
| VideoGen API | video-api.holdfastmusic.it | 8000 |
| VideoGen UI | video.holdfastmusic.it | 5173 |
| Bot / ReelForge | bot.holdfastmusic.it | 8765 |
| n8n | n8n.holdfastmusic.it | 5678 |
| Postiz | postiz.holdfastmusic.it | 5000 |
| Paperclip | paperclip.holdfastmusic.it | 3100 |
| Drone (DroneOps) | drone.holdfastmusic.it | 8501 |
| Media | media.holdfastmusic.it | 8088 |

Tunnel: Cloudflare (`d2c659ec-5a66-44e3-8071-fe2a8d02bef7`)

---

## Vault Obsidian locale
Percorso: `~/Documents/VaultFrancesco`

Struttura attesa:
- `00-Inbox/README.md` — briefing attivo corrente
- `Missioni/` — missioni drone Nevaproject (DJI M4, scenari STS-01/STS-02)
- `Kujan/` — release notes e roadmap Kujan
- `CLAUDE.md` — questo file (istruzioni globali per Claude Code CLI)

Per caricare il contesto del vault in una sessione locale, usare l'alias `claude-brain` (vedi sotto).

---

## Setup alias locale (Mac)

Incolla in `~/.zshrc`:

```bash
alias claude-brain='cd ~/Documents/VaultFrancesco && (npx obsidian-mcp ~/Documents/VaultFrancesco > /dev/null 2>&1 &) && claude'
```

Poi: `source ~/.zshrc`

Questo alias:
1. Fa cd nel vault → Claude Code legge automaticamente `CLAUDE.md` da lì
2. Avvia `obsidian-mcp` in background per tool access ai file del vault
3. Lancia `claude` nella directory corretta

### Se CLAUDE.md non esiste nel vault
```bash
cp ~/Documents/VaultFrancesco/../digital-legacy/CLAUDE.md ~/Documents/VaultFrancesco/CLAUDE.md
```
Poi personalizzalo con missione corrente e ultima release Kujan.

---

## Note operative
- **CCR (claude.ai/code)** non può fare SSH in uscita per policy di rete — non può connettersi al VPS direttamente
- Per sessioni sempre-on anche a Mac spento → installare Claude Code CLI sul VPS + tmux (vedere `scripts/vps-setup.md`)
- Il Dell di casa (192.168.1.46) è DISMESSO — solo backup LAN
- **TODO**: `deploy.sh` di CFO-AI punta ancora a 192.168.1.46 — fixare aprendo sessione su repo `holdfastmusic/cfo-ai`
- Utente: Francesco Fabbri / francesco.fabbri@gmail.com / Nevaproject
