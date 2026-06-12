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

## Ecosistema holdfastmusic.it (server Dell self-hosted)

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
| Drone | drone.holdfastmusic.it | 8501 |
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
- Il server Dell è sempre acceso; le sessioni CCR su Claude.ai/code accedono a questo repo via GitHub
- Per sessioni sempre-on anche a Mac spento → usare Claude Code su VPS (vedere `scripts/vps-setup.md`)
- Utente: Francesco Fabbri / francesco.fabbri@gmail.com / Nevaproject
