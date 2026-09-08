# Claude Code CLI sul VPS — sessioni sempre-on

Il VPS ospita già tutti i servizi (Kujan, Kinsu, n8n, Postiz, ecc.).
Installare Claude Code CLI lì significa: agenti attivi 24/7, accesso diretto
ai servizi interni, raggiungibile da qualsiasi device anche con Mac spento.

---

## Setup (una tantum sul VPS)

```bash
# 1. Installa Node.js se non c'è
node --version 2>/dev/null || (curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - && sudo apt install -y nodejs)

# 2. Installa Claude Code CLI
npm install -g @anthropic-ai/claude-code

# 3. API key (mettila in .bashrc/.zshrc per persistenza)
echo 'export ANTHROPIC_API_KEY="sk-ant-..."' >> ~/.bashrc
source ~/.bashrc

# 4. Verifica
claude --version
```

---

## Sessioni persistenti con tmux

Senza tmux la sessione Claude muore quando chiudi SSH.

```bash
# Crea una sessione persistente
tmux new -s brain

# Dentro tmux: avvia Claude nel repo
cd ~/digital-legacy && claude

# Detach (sessione rimane attiva in background)
# Ctrl+B poi D

# Riconnetti da qualsiasi device in qualsiasi momento
ssh user@<ip-vps> -t "tmux attach -t brain"
```

Se la sessione è già detached e vuoi crearne una nuova:
```bash
tmux new -s brain2
```

---

## Alias sul VPS (in ~/.bashrc)

```bash
# Claude nel repo digital-legacy
alias claude-brain='cd ~/digital-legacy && claude'

# Claude con un repo specifico
alias claude-kujan='cd ~/kujan && claude'
```

---

## Accesso da mobile

Dal telefono o iPad con SSH:
- **iOS**: [Blink Shell](https://blink.sh) o [Termius](https://termius.com)
- **Android**: Termux o JuiceSSH

```bash
# Una volta connesso in SSH
tmux attach -t brain   # riprende la sessione esistente
```

---

## Opzione alternativa: Claude Code on the Web

Le sessioni su `claude.ai/code` girano già su server Anthropic — zero setup,
zero costi aggiuntivi. Il contesto è nel `CLAUDE.md` di questo repo.

**Limitazione**: ogni sessione CCR è un container effimero isolato,
non può chiamare direttamente i servizi sul VPS (Kujan :3000, n8n :5678, ecc.)
senza tunnel esplicito.

**Raccomandazione**: usa CCR per sviluppo/codice, Claude CLI sul VPS
per automazioni e agenti che devono toccare i servizi interni.
