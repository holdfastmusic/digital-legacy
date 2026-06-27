# Digital Legacy — Piano Completo per Analisi

**Data**: 27 giugno 2026  
**Autore**: Francesco Fabbri / Nevaproject  
**Repo**: github.com/holdfastmusic/digital-legacy

---

## 1. COS'E'

App web per la **gestione del patrimonio digitale post-mortem** (testamento digitale).

Un utente cataloga i propri asset digitali (account social, email, crypto wallet, cloud storage, conti bancari online), designa beneficiari per ciascuno, e imposta un "dead man's switch" basato su inattività: se non accede per N giorni, il sistema notifica i beneficiari e consegna le istruzioni di accesso.

---

## 2. STACK TECNICO ATTUALE

```
Backend:   Python/Flask + SQLAlchemy + SQLite
Frontend:  React SPA precompilata (sorgenti non nel repo)
Auth:      JWT (7 giorni)
Cifratura: Fernet (AES-128-CBC)
Deploy:    python main.py (porta 5000)
```

### Modelli dati

| Modello | Ruolo |
|---|---|
| User | Utente principale, auth con bcrypt |
| DigitalAsset | Asset digitale (9 tipi: social, email, crypto, financial, cloud, domain, subscription, gaming, other) |
| Beneficiary | Persona designata (nome, email, telefono, relazione) |
| AssetAssignment | Collegamento N:N asset→beneficiario con istruzioni specifiche |
| SuccessionPlan | Piano successione: trigger_days (1-365), status (active/triggered/completed), last_activity |

### API REST

| Endpoint | Metodi |
|---|---|
| `/api/auth/register` | POST |
| `/api/auth/login` | POST |
| `/api/auth/verify` | GET |
| `/api/digital-assets` | GET, POST |
| `/api/digital-assets/:id` | GET, PUT, DELETE |
| `/api/digital-assets/types` | GET |
| `/api/beneficiaries` | GET, POST |
| `/api/beneficiaries/:id` | GET, PUT, DELETE |
| `/api/assignments` | GET, POST |
| `/api/assignments/:id` | GET, PUT, DELETE |
| `/api/succession-plan` | GET, POST, PUT, DELETE |
| `/api/succession-plan/activity` | POST |
| `/api/succession-plan/status` | GET |
| `/api/health` | GET |

---

## 3. BUG CRITICI TROVATI E FIXATI

### 3.1 Chiave di cifratura volatile (FIXATO)

**Prima**: `ENCRYPTION_KEY = Fernet.generate_key()` — rigenerata ad ogni avvio del server. Tutti i dati cifrati diventavano illeggibili al restart.

**Dopo**: legge da `os.environ['ENCRYPTION_KEY']`. Se assente, genera e stampa un warning.

### 3.2 JWT secret hardcoded (FIXATO)

**Prima**: `JWT_SECRET = 'digital_legacy_secret_key_2024'` — hardcoded nel codice.

**Dopo**: `JWT_SECRET = os.environ.get('JWT_SECRET', 'digital_legacy_secret_key_2024')` — fallback al default per dev.

### 3.3 require_auth senza @wraps (FIXATO)

Flask richiede `@wraps(f)` sui decorator per preservare i nomi delle route. Senza, collisioni a runtime con più route decorate.

### 3.4 Trigger di inattività assente (FIXATO)

**Prima**: il campo `trigger_days` esisteva nel modello ma nessun processo lo controllava.

**Dopo**: aggiunto `src/jobs/__init__.py` — script eseguibile via cron:
- Controlla tutti i piani attivi
- Warning email al 66% del trigger (es. giorno 60 su 90)
- Trigger al 100%: cambia status a "triggered" e notifica tutti i beneficiari con lista asset assegnati
- Modalità dry-run se SMTP non configurato

---

## 4. ANALISI COMPETITIVA

### 4.1 Mercato globale — $13-23 miliardi, 15-17% CAGR

| Player | Prezzo | Status |
|---|---|---|
| Google Inactive Account Manager | Gratis | Trigger 3-18 mesi, 10 contatti, solo Google |
| Apple Digital Legacy | Gratis | 5 contatti, solo iCloud |
| Everplans | $27-100/anno | Acquisito da Precoa (ott 2024) |
| Clocr | $60/anno | Crypto/NFT, AI messaging |
| Empathy | B2B assicurazioni | $72M Series C (2024) |
| Inheriti 2.0 | N/D | Belgio, EU-first |
| 1Password/Proton Pass | In-app | Emergency access integrato |

### 4.2 Mercato italiano — VUOTO

**Zero startup italiane dedicate al digital legacy** (ricerca su 30+ fonti).

| Attore italiano | Offerta | Prodotto digitale |
|---|---|---|
| Studi legali | Consulenza successione digitale | No |
| Consiglio Nazionale del Notariato | Guida + protocollo con Microsoft/Google (in sviluppo) | No |
| Banche (Widiba, Hype, Flowe) | Nessuna | No |
| Assicurazioni italiane | Nessuna | No |

### 4.3 Quadro legale italiano

- **Art. 2-terdecies Codice Privacy** (D.Lgs. 101/2018): gli eredi possono esercitare diritti GDPR sui dati del defunto
- **Sentenze**: Milano (feb 2021, landmark), Bologna (2021), Roma (2022), Venezia (2025) — i dati digitali "sopravvivono" al titolare
- **Limite critico**: nessuna legge organica sulla successione digitale; ogni caso richiede intervento giudiziario o notarile
- **Crypto**: tassati al 33% dal 2026, parte dell'asse ereditario

---

## 5. MODELLI DI BUSINESS POSSIBILI

### Modello A — SaaS B2C diretto
- **Target**: consumatori italiani
- **Prezzo**: €5-10/mese o €50-80/anno
- **Pro**: scalabile, mercato EU scoperto
- **Contro**: Apple/Google gratis coprono il caso base; barriera di fiducia alta; CAC elevato

### Modello B — B2B via notai e studi legali (RACCOMANDATO)
- **Target**: 35.000 notai italiani + studi legali con pratiche successorie
- **Prezzo**: €500-2.000/anno per studio (white-label)
- **Pro**: canale di fiducia naturale; il Notariato sta attivamente cercando partner tecnologici; €300 miliardi di trasferimento intergenerazionale entro 2033
- **Contro**: ciclo di vendita lungo; adozione tecnologica lenta tra notai

### Modello C — Verticale crypto
- **Target**: holder crypto italiani senza piano di successione
- **Prezzo**: €9-15/mese
- **Pro**: problema acutissimo (crypto persi per sempre); utenti pagano volentieri; integrazione Ledger/Trezor come differenziatore
- **Contro**: mercato di nicchia; volatilità crypto influenza retention

### Modello D — B2B2C via banche/assicurazioni
- **Target**: neobank e assicurazioni italiane come canale di distribuzione
- **Prezzo**: licensing/revenue share
- **Pro**: base clienti enorme; gap di mercato confermato
- **Contro**: integrazione lunga; compliance pesante

---

## 6. RISCHI E CRITICITA'

### Rischio 1 — Fiducia
Nessuno vuole salvare password su un servizio sconosciuto. Mitigazione: partnership notarili, audit di sicurezza terzo, open source della componente crypto.

### Rischio 2 — Big Tech cannibalizzano
Google e Apple espandono il loro legacy contact a terze parti → mercato consumer svanisce. Mitigazione: B2B (i notai non saranno sostituiti da Apple).

### Rischio 3 — Complessità legale
La validità giuridica del lascito digitale in Italia è ancora grigia. Mitigazione: partnership con studio legale specializzato, validazione notarile.

### Rischio 4 — Sicurezza come responsabilità
Un breach = credenziali di decine di account esposti. Mitigazione: cifratura end-to-end, zero-knowledge architecture, SOC2/ISO27001.

---

## 7. ROADMAP TECNICA

### Fase 1 — MVP funzionante (completata/in corso)
- [x] API REST completa (CRUD asset, beneficiari, assegnazioni, piano successione)
- [x] Auth JWT
- [x] Cifratura credenziali con Fernet
- [x] Fix chiave cifratura persistente
- [x] Job trigger inattività + notifiche email

### Fase 2 — Prodotto minimo vendibile
- [ ] Deploy su VPS con HTTPS (Cloudflare tunnel già disponibile)
- [ ] Frontend React: riscrivere da sorgenti o rebuild
- [ ] Verifica identità beneficiario (OTP email prima di consegnare credenziali)
- [ ] 2FA per utente principale (TOTP)
- [ ] Cron job automatico per check inattività (systemd timer o cron)

### Fase 3 — Differenziazione
- [ ] Integrazione SPID/CIE per verifica identità beneficiari italiani
- [ ] Supporto crypto wallet (Ledger/Trezor import chiavi pubbliche)
- [ ] Dashboard notaio (white-label)
- [ ] Audit trail immutabile (chi ha accesso a cosa e quando)
- [ ] Multi-lingua (IT/EN)

### Fase 4 — Scale
- [ ] Migrazione da SQLite a PostgreSQL
- [ ] Zero-knowledge encryption (client-side)
- [ ] Mobile app (React Native)
- [ ] Integrazioni bancarie PSD2
- [ ] Certificazione SOC2 / ISO 27001

---

## 8. UNIT ECONOMICS (stima Modello B — B2B notai)

| Metrica | Valore |
|---|---|
| TAM Italia | 35.000 studi notarili |
| Prezzo medio | €1.000/anno |
| Target anno 1 | 50 studi (0.14%) |
| ARR anno 1 | €50.000 |
| Target anno 3 | 500 studi (1.4%) |
| ARR anno 3 | €500.000 |
| Costi infra | ~€100/mese (VPS + email) |
| Margine lordo | >90% |
| Break-even | ~30 clienti |

---

## 9. DOMANDE APERTE PER VALIDAZIONE

1. I notai italiani adotterebbero un SaaS esterno o vogliono on-premise?
2. Il protocollo Notariato-Microsoft-Google è aperto a partner tecnologici terzi?
3. Quale livello di certificazione di sicurezza richiedono gli studi notarili?
4. Il mandato post-mortem è sufficiente come base legale o serve testamento olografo?
5. Quanti crypto holder italiani hanno un piano di successione oggi? (stima: <5%)

---

## 10. CONCLUSIONE

**Il mercato esiste, è in crescita, e l'Italia è scoperta.**

Il prodotto attuale è un MVP funzionante con i bug critici ora fixati. Il percorso più veloce al revenue è il Modello B (B2B notai) con validazione tramite 3-5 studi pilota.

Il rischio maggiore non è tecnico — è la fiducia. Senza un partner istituzionale (notaio, banca, assicurazione), il consumer italiano non affiderà le proprie password a un servizio sconosciuto.
