# Digital Legacy — Piano Completo per Analisi (v2, revisionato dopo critica esterna)

**Data**: 4 agosto 2026
**Autore**: Francesco Fabbri / Nevaproject
**Repo**: github.com/holdfastmusic/digital-legacy

> **Nota v2**: questa versione integra una revisione critica (Gemini) della v1 del 27 giugno 2026,
> che ha individuato un errore di TAM, una lacuna di sicurezza strutturale e un rischio legale non
> affrontato (Sezione 11), e una proposta di ridimensionamento verso un'architettura modulare a
> basso rischio, estesa oltre i soli asset "digitali" a conti, assicurazioni e accessi in generale
> (Sezione 12).

---

## 1. COS'E'

App web per la **gestione del patrimonio digitale post-mortem** (testamento digitale).

Un utente cataloga i propri asset digitali (account social, email, crypto wallet, cloud storage,
conti bancari online), designa beneficiari per ciascuno, e imposta un "dead man's switch" basato
su inattività: se non accede per N giorni, il sistema notifica i beneficiari e consegna le
istruzioni d'accesso.

---

## 2. STACK TECNICO ATTUALE

```
Backend:   Python/Flask + SQLAlchemy + SQLite
Frontend:  React SPA precompilata (sorgenti non nel repo)
Auth:      JWT (7 giorni)
Cifratura: Fernet (AES-128-CBC), server-side
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

### Cosa viene effettivamente cifrato (dettaglio verificato nel codice)

L'unico campo cifrato in tutto il sistema è `DigitalAsset.credentials_encrypted` (Fernet).
`username` e `url` restano in chiaro. Il punto critico: **l'email di trigger di inattività
(`jobs/__init__.py`) non invia mai le credenziali decifrate ai beneficiari** — invia solo nome
asset, tipo e istruzioni a livello di assegnazione, più una riga generica "contatta il gestore del
servizio". Non esiste nemmeno un endpoint che permetta a un beneficiario di recuperare le
credenziali. In pratica il vault di credenziali esiste ma non viene mai consegnato a nessuno nel
flusso attuale — è rischio (dati sensibili cifrati server-side, a riposo) senza un beneficio
corrispondente nel prodotto così com'è.

---

## 3. BUG CRITICI TROVATI E FIXATI

### 3.1 Chiave di cifratura volatile (FIXATO)
**Prima**: `ENCRYPTION_KEY = Fernet.generate_key()` — rigenerata ad ogni avvio del server. Tutti i
dati cifrati diventavano illeggibili al restart.
**Dopo**: legge da `os.environ['ENCRYPTION_KEY']`. Se assente, genera e stampa un warning.

### 3.2 JWT secret hardcoded (FIXATO)
**Prima**: `JWT_SECRET = 'digital_legacy_secret_key_2024'` — hardcoded nel codice.
**Dopo**: `JWT_SECRET = os.environ.get('JWT_SECRET', 'digital_legacy_secret_key_2024')` —
fallback al default solo per dev.

### 3.3 require_auth senza @wraps (FIXATO)
Flask richiede `@wraps(f)` sui decorator per preservare i nomi delle route. Senza, collisioni a
runtime con più route decorate.

### 3.4 Trigger di inattività assente (FIXATO)
**Prima**: il campo `trigger_days` esisteva nel modello ma nessun processo lo controllava.
**Dopo**: aggiunto `src/jobs/__init__.py` — script eseguibile via cron:
- Controlla tutti i piani attivi
- Warning email al 66% del trigger (es. giorno 60 su 90)
- Trigger al 100%: cambia status a "triggered" e notifica tutti i beneficiari con lista asset
  assegnati (senza credenziali — vedi Sezione 2)
- Modalità dry-run se SMTP non configurato

**Nota sui falsi positivi (non ancora risolto, vedi Sezione 11.4)**: il trigger attuale è un
semplice conteggio giorni da `last_activity`. Non distingue tra "utente morto" e "utente in
vacanza/ospedale/senza accesso a internet". Un trigger falso notifica i beneficiari e consegna
istruzioni mentre l'utente è vivo — rischio di prodotto serio, non solo tecnico.

---

## 4. ANALISI COMPETITIVA

### 4.1 Mercato globale — $12-23 miliardi, 15-17% CAGR (stime variabili, mercato frammentato)

| Player | Prezzo | Status |
|---|---|---|
| Google Inactive Account Manager | Gratis | Trigger 3-18 mesi, 10 contatti, solo dati Google |
| Apple Digital Legacy | Gratis | 5 Legacy Contact, richiede certificato di morte, solo iCloud |
| Everplans | $27-100/anno | Acquisito da Precoa (ott 2024) |
| Clocr | $60/anno | Crypto/NFT, AI messaging |
| Empathy | B2B assicurazioni | $72M Series C (2024) |
| Inheriti 2.0 | N/D | Belgio, EU-first |
| 1Password/Proton Pass | In-app | Emergency access integrato |

**Differenza strutturale importante**: Apple e Google possono "rilasciare l'accesso" al legacy
contact perché **sono loro stessi il fornitore del servizio** — mediano l'accesso internamente
senza mai esporre una password in chiaro. Digital Legacy non è il fornitore di Facebook, di un
exchange crypto o di una banca: l'unica cosa che può realisticamente trasmettere a un erede è (a)
una credenziale vera e propria, con il rischio legale che comporta (Sezione 11.3), oppure (b)
istruzioni su come procedere per vie legittime. Questo vincolo strutturale rende il vault di
credenziali intrinsecamente più pericoloso — e meno indispensabile al prodotto — di quanto
sembrasse nella v1 del piano. **Everplans**, in particolare, è il precedente più vicino alla
Sezione 12: copre non solo account digitali ma l'intero "patrimonio delle informazioni" (conti,
assicurazioni, documenti legali) senza necessariamente conservare password.

### 4.2 Mercato italiano — quasi vuoto lato prodotto

**Zero startup italiane dedicate al digital legacy** (ricerca su 30+ fonti).

| Attore italiano | Offerta | Prodotto digitale |
|---|---|---|
| Studi legali | Consulenza successione digitale | No |
| Consiglio Nazionale del Notariato | Guida + protocollo con Microsoft/Google (in sviluppo) | No |
| Banche (Widiba, Hype, Flowe) | Nessuna | No |
| Assicurazioni italiane | Nessuna | No |

**Attenzione (vedi 11.6)**: il protocollo Notariato–Microsoft–Google in sviluppo non è solo
un'opportunità di partnership — è anche una minaccia diretta. Se diventa uno standard nazionale
gestito dagli stessi big tech, un prodotto terzo come Digital Legacy rischia di essere bypassato
completamente su quel canale.

### 4.3 Quadro legale italiano

- **Art. 2-terdecies Codice Privacy** (D.Lgs. 101/2018): gli eredi possono esercitare diritti GDPR
  sui dati del defunto
- **Sentenze**: Milano (feb 2021, landmark), Bologna (2021), Roma (2022), Venezia (2025) — i dati
  digitali "sopravvivono" al titolare
- **Limite critico**: nessuna legge organica sulla successione digitale; ogni caso richiede
  intervento giudiziario o notarile
- **Rischio penale non affrontato nella v1**: vedi Sezione 11.3 — Art. 615-ter c.p.
- **Crypto**: tassati al 33% dal 2026, parte dell'asse ereditario
- **Barriera culturale**: solo ~13% degli italiani redige un testamento tradizionale. Il
  "testamento digitale" è un concetto ancora meno familiare — impatta l'adozione consumer diretta
  più di quanto stimato in v1 (vedi 11.5)

---

## 5. MODELLI DI BUSINESS POSSIBILI

### Modello A — SaaS B2C diretto
- **Target**: consumatori italiani
- **Prezzo**: €5-10/mese o €50-80/anno
- **Pro**: scalabile, mercato EU scoperto
- **Contro**: Apple/Google gratis coprono il caso base; barriera di fiducia alta; CAC elevato;
  barriera culturale del testamento (11.5)

### Modello B — B2B via notai e studi legali (RACCOMANDATO)
- **Target**: **~5.000 notai italiani** (corretto da 35.000 nella v1 — vedi 11.1) + studi legali
  con pratiche successorie
- **Prezzo**: €500-2.000/anno per studio (white-label)
- **Pro**: canale di fiducia naturale; il Notariato sta cercando partner tecnologici; €300 miliardi
  di trasferimento intergenerazionale entro 2033
- **Contro**: ciclo di vendita lungo; adozione tecnologica lenta tra notai; rischio di essere
  bypassati dal protocollo Notariato-Microsoft-Google (11.6)

### Modello C — Verticale crypto
- **Target**: holder crypto italiani senza piano di successione
- **Prezzo**: €9-15/mese
- **Pro**: problema acutissimo (crypto persi per sempre); utenti pagano volentieri; integrazione
  Ledger/Trezor come differenziatore
- **Contro**: mercato di nicchia; volatilità crypto influenza retention

### Modello D — B2B2C via banche/assicurazioni
- **Target**: neobank e assicurazioni italiane come canale di distribuzione
- **Prezzo**: licensing/revenue share
- **Pro**: base clienti enorme; gap di mercato confermato
- **Contro**: integrazione lunga; compliance pesante

---

## 6. RISCHI E CRITICITA'

### Rischio 1 — Fiducia
Nessuno vuole salvare password su un servizio sconosciuto. Mitigazione più efficace: **non
salvare password affatto** nel prodotto core (vedi Sezione 12), oltre a partnership notarili e
audit di sicurezza terzo.

### Rischio 2 — Big Tech cannibalizzano
Google e Apple espandono il loro legacy contact a terze parti → mercato consumer svanisce.
Mitigazione: B2B (i notai non saranno sostituiti da Apple), ma vedi anche 11.6.

### Rischio 3 — Complessità legale
La validità giuridica del lascito digitale in Italia è ancora grigia, e la condivisione di
credenziali comporta un rischio penale specifico (11.3). Mitigazione: partnership con studio
legale specializzato, validazione notarile, e ridisegno del prodotto per non trasmettere mai
credenziali (Sezione 12).

### Rischio 4 — Sicurezza come responsabilità
Un breach = credenziali di decine di account esposti — **solo se il prodotto le conserva**.
Mitigazione architetturale preferita: non conservarle nel modulo core; se in futuro si
reintroduce un vault, farlo zero-knowledge fin dal primo giorno (non come feature di Fase 4).

### Rischio 5 — Falsi positivi del dead man's switch (nuovo, da 11.4)
Vacanza, ricovero ospedaliero, smarrimento del telefono → trigger involontario mentre l'utente è
vivo, con conseguenze potenzialmente gravi (notifica ai familiari, avvio di procedure). Va
mitigato con conferma multi-canale e periodo di grazia (vedi 11.4).

---

## 7. ROADMAP TECNICA (rivista — vedi Sezione 12 per il razionale)

### Fase 1 — MVP: modulo core "Istruzioni & Contatti" (no credenziali, categorie estese)
- [x] API REST completa (CRUD asset, beneficiari, assegnazioni, piano successione)
- [x] Auth JWT
- [x] Fix chiave cifratura persistente / JWT secret / require_auth
- [x] Job trigger inattività + notifiche email
- [ ] **Rimuovere lo storage di credenziali dal modulo core** (`credentials_encrypted`,
      `encrypt_credentials`/`decrypt_credentials`, dipendenza `cryptography`) — voce = nome,
      categoria, riferimento (URL/IBAN/numero polizza/username), istruzioni testuali, mai password
- [ ] **Estendere la tassonomia oltre gli "asset digitali"** (vedi 12.4): aggiungere categorie
      conto corrente/deposito, polizza assicurativa, utenza/abbonamento, accesso ad app
      professionali/gestionali, documenti legali — riusando lo stesso modello dati (Sezione 12.4)
- [ ] Conferma multi-canale per il trigger di inattività + periodo di grazia (mitigazione falsi
      positivi, 11.4)
- [ ] Deploy su VPS con HTTPS (Cloudflare tunnel già disponibile)
- [ ] Frontend React: riscrivere da sorgenti o rebuild, adattato al modello senza password e alle
      nuove categorie
- [ ] Verifica identità beneficiario (OTP email prima di consegnare le istruzioni)
- [ ] 2FA per utente principale (TOTP)
- [ ] Cron job automatico per check inattività (systemd timer o cron)

### Fase 2 — Differenziazione B2B
- [ ] Integrazione SPID/CIE per verifica identità beneficiari italiani
- [ ] Dashboard notaio (white-label)
- [ ] Audit trail immutabile (chi ha accesso a cosa e quando)
- [ ] Multi-lingua (IT/EN)
- [ ] Revisione legale formale del testo delle istruzioni consegnate (per restare nel perimetro
      lecito, vedi 11.3)

### Fase 3 — Modulo avanzato opzionale "Vault sicuro"
- [ ] Cifratura **zero-knowledge client-side** (mai server-side) per chi vuole comunque salvare
      credenziali — reintrodotta solo qui, fatta bene, non come nella v1
- [ ] Valutare in alternativa l'integrazione con password manager esistenti (1Password, Proton
      Pass) invece di ricostruire un vault proprietario
- [ ] Supporto crypto wallet (Ledger/Trezor import chiavi pubbliche)

### Fase 4 — Scale
- [ ] Migrazione da SQLite a PostgreSQL
- [ ] Mobile app (React Native)
- [ ] Integrazioni bancarie PSD2
- [ ] Certificazione SOC2 / ISO 27001

---

## 8. UNIT ECONOMICS (Modello B — B2B notai, ricalcolato con TAM corretto)

| Metrica | v1 (errata) | v2 (corretta) |
|---|---|---|
| TAM Italia | 35.000 studi notarili | **~5.000 notai** |
| Prezzo medio | €1.000/anno | €1.000/anno |
| Target anno 1 | 50 studi (0,14%) | 50 studi (**1,0%** del TAM reale) |
| ARR anno 1 | €50.000 | €50.000 (penetrazione richiesta molto più alta: 1% non 0,14%) |
| Target anno 3 | 500 studi (1,4%) | 500 studi (**10%** del TAM reale — obiettivo molto ambizioso) |
| ARR anno 3 | €500.000 | €500.000 (stesso ARR ma su un mercato 7x più piccolo → execution risk molto maggiore) |
| Costi infra | ~€100/mese | ~€100/mese |
| Costi assicurazione/compliance (nuovo, 11.7) | non considerati | da preventivare: RC professionale, eventuale audit di sicurezza — impatta il margine dichiarato del 90% |
| Margine lordo | >90% | da rivedere al netto di 11.7, probabilmente 70-85% |
| Break-even | ~30 clienti | invariato in valore assoluto, ma rappresenta una quota molto più alta del mercato reale |

**Implicazione principale**: con un TAM reale di ~5.000 notai invece di 35.000, l'obiettivo di
500 clienti all'anno 3 non è più l'1,4% del mercato ma il **10%** — un obiettivo enormemente più
aggressivo. Questo non rende il piano impossibile, ma richiede assunzioni di crescita molto più
conservative o un allargamento del target (studi legali generalisti, non solo notai). L'estensione
di prodotto in Sezione 12 (oltre il digitale puro) allarga anche il mercato indirizzabile: uno
strumento che copre conti, polizze e accessi diventa rilevante anche per commercialisti e
consulenti patrimoniali, non solo per notai.

---

## 9. DOMANDE APERTE PER VALIDAZIONE

1. I notai italiani adotterebbero un SaaS esterno o vogliono on-premise?
2. Il protocollo Notariato-Microsoft-Google è aperto a partner tecnologici terzi, o li esclude
   (11.6)?
3. Quale livello di certificazione di sicurezza richiedono gli studi notarili?
4. Il mandato post-mortem è sufficiente come base legale o serve testamento olografo?
5. Quanti crypto holder italiani hanno un piano di successione oggi? (stima: <5%)
6. **Nuovo**: un parere legale formale conferma che un modulo "solo istruzioni, mai credenziali"
   evita l'esposizione ex Art. 615-ter c.p.?
7. **Nuovo**: qual è un periodo di grazia/meccanismo di conferma accettabile per ridurre i falsi
   positivi del trigger senza renderlo inefficace?
8. **Nuovo (12.4)**: un "inventario patrimoniale + accessi" più ampio (conti, polizze, app) compete
   con strumenti già usati da notai/commercialisti (es. software di gestione successioni), o li
   completa?
9. **Nuovo (12.5)**: un posizionamento "mappa di famiglia utile anche in vita" richiede un modello
   di condivisione/co-visibilità con i familiari prima del decesso — un cambio di prodotto non
   banale rispetto al solo trigger post-mortem. Va validato con utenti reali nella fascia 50-60
   prima di investirci: preferiscono uno strumento condiviso da subito, o mantengono la logica
   "segreto fino alla morte" del modello attuale?

---

## 10. CONCLUSIONE (rivista)

**Il mercato esiste ed è in crescita, ma l'Italia è più piccola e più difficile da penetrare di
quanto stimato nella v1.** Il TAM B2B notai è ~5.000 soggetti, non 35.000, il che alza
sensibilmente la barra di execution del Modello B.

Il prodotto attuale è un MVP funzionante con i bug critici del ciclo precedente fixati, ma
conserva una vulnerabilità architetturale — il vault di credenziali server-side — che non è mai
stata necessaria al flusso reale del prodotto e che espone a rischio legale (Art. 615-ter) e di
sicurezza senza un beneficio corrispondente. La raccomandazione (Sezione 12) è di **ridurre lo
scope tecnico del MVP** eliminando lo storage di credenziali dal modulo core, avvicinandosi al
modello "istruzioni + designazione + trigger" di Apple/Google, e contemporaneamente **allargare lo
scope di prodotto** oltre i soli asset digitali a conti, assicurazioni e accessi in generale — le
due mosse sono coerenti, perché una volta tolte le password il prodotto non ha più motivo di
limitarsi al "digitale".

Il rischio maggiore resta la fiducia — ma un prodotto che strutturalmente non può perdere
credenziali (perché non le conserva) affronta quel rischio meglio di uno che promette sicurezza
senza un'architettura zero-knowledge a supporto. Il percorso più veloce al revenue resta il
Modello B (B2B notai), validato con 3-5 studi pilota, ma con obiettivi di penetrazione ricalibrati
sul TAM reale.

---

## 11. CRITICA ESTERNA (Gemini) E CORREZIONI — sintesi

La v1 di questo piano è stata sottoposta a revisione esterna. Ecco i punti sollevati e come sono
stati integrati:

### 11.1 — Errore di TAM
35.000 notai italiani era sbagliato: il numero reale è **~5.000**. Corretto in Sezione 5 e 8.
L'obiettivo del 10% di penetrazione all'anno 3 (invece dell'1,4% originale) è molto più ambizioso
e va comunicato come tale, non nascosto dietro il numero sbagliato.

### 11.2 — Architettura di sicurezza inadeguata
Nella v1 la cifratura zero-knowledge (client-side) era relegata alla Fase 4 ("Scale"), mentre il
prodotto già oggi cifra le credenziali solo server-side. Per un prodotto che custodisce
credenziali d'accesso, la cifratura server-side è considerata inadeguata dallo standard di
settore. **Corretto**: vedi Sezione 12 — la soluzione adottata non è "spostare zero-knowledge in
Fase 1", ma **eliminare lo storage di credenziali dal core** ed eventualmente reintrodurlo come
modulo avanzato zero-knowledge, il che risolve il problema in modo più radicale e con meno
rischio.

### 11.3 — Rischio penale Art. 615-ter c.p.
Fornire a un beneficiario le credenziali per accedere agli account del defunto può configurare
accesso abusivo a un sistema informatico, un reato in Italia. La v1 non affrontava questo rischio.
**Corretto**: il modulo core (Sezione 12) non trasmette mai credenziali, solo istruzioni testuali
su come procedere (es. contattare l'assistenza della piattaforma, presentare un certificato di
morte, rivolgersi a un notaio) — il che è già in linea con quanto effettivamente fa il codice
attuale (vedi Sezione 2). Resta comunque necessario un parere legale formale prima del lancio
(domanda aperta 9.6).

### 11.4 — Falsi positivi del dead man's switch
Non affrontato in v1. Un trigger di inattività basato solo su un conteggio di giorni scatta anche
per vacanza, ricovero, smarrimento del dispositivo. **Aggiunto** in Sezione 6 (Rischio 5) e in
Roadmap Fase 1: conferma multi-canale (email + SMS/push) e periodo di grazia prima di considerare
il trigger definitivo.

### 11.5 — Barriera culturale
Solo il 13% degli italiani fa testamento tradizionale; il testamento digitale è un concetto ancora
più estraneo. La v1 non quantificava questo effetto sull'adozione B2C. **Aggiunto** in Sezione 4.3
e riflesso nella preferenza per il Modello B (B2B) rispetto al Modello A (B2C diretto).

### 11.6 — Il protocollo Notariato-Microsoft-Google come minaccia, non solo opportunità
La v1 presentava il protocollo in sviluppo solo come un'opportunità di partnership. **Corretto**:
se diventa lo standard nazionale gestito direttamente dai big tech insieme al Notariato, un
prodotto terzo rischia di essere bypassato su quel canale specifico. Va monitorato come rischio
competitivo, non solo come opportunità (Sezione 4.2, domanda aperta 9.2).

### 11.7 — Margini di errore nell'unit economics
Il margine lordo >90% dichiarato in v1 non considerava costi di assicurazione di responsabilità
professionale e compliance, rilevanti per un prodotto B2B venduto a notai che maneggia dati
sensibili. **Aggiunto** in Sezione 8: margine realistico stimato 70-85% al netto di questi costi,
da verificare con preventivi reali.

---

## 12. PROPOSTA: ARCHITETTURA MODULARE SEMPLIFICATA E AMPLIAMENTO DI SCOPE (analisi pivot)

### La domanda
Ha senso semplificare il prodotto, o farlo a moduli, così da poterlo usare anche come app semplice
in stile Apple Digital Legacy — eventualmente ampliata anche a conti correnti, assicurazioni,
accessi ad app e non solo ad asset "digitali" in senso stretto? È il caso di fare un pivot?

### Cosa fa davvero il codice oggi (verificato)
`DigitalAsset.credentials_encrypted` è l'unico campo cifrato di tutto il sistema. L'email di
trigger di inattività **non invia mai le credenziali decifrate**: manda solo nome asset, tipo e
istruzioni di assegnazione, più un messaggio generico. Non esiste alcun endpoint che permetta a un
beneficiario di recuperare credenziali. In pratica **il prodotto si comporta già** come un sistema
"istruzioni + designazione", con un vault di credenziali opzionale che di fatto non viene mai
consegnato a nessuno nel flusso reale.

### Perché Apple/Google non salvano credenziali (e perché Digital Legacy lo fa)
Apple e Google possono "sbloccare l'accesso" al legacy contact perché sono loro stessi il
fornitore del servizio: mediano l'accesso internamente, senza mai esporre una password. Digital
Legacy non è il fornitore di Facebook, di un exchange crypto o di una banca — l'unica cosa che può
davvero trasmettere è (a) una credenziale vera e propria, col rischio penale di 11.3, oppure (b)
istruzioni su come procedere per vie legittime. Questo è un vincolo strutturale, non una scelta di
design arbitraria — e vale anche per conti bancari, polizze e app: il prodotto non è il fornitore
di nessuno di questi servizi, quindi il suo ruolo naturale è sempre "indice + istruzioni", mai
"cassaforte di accessi".

### Proposta: due moduli, non un pivot di business

**Modulo core (MVP) — "Inventario & Contatti", stile Apple/Google ma a scope più ampio**
- Nessuna credenziale salvata: si elimina `credentials_encrypted`, le funzioni
  `encrypt_credentials()`/`decrypt_credentials()` e la dipendenza `cryptography` — modifica
  isolata e piccola (un campo del modello, un file di route, circa 30 righe)
- Voce = nome, categoria, riferimento pubblico (URL, IBAN, numero polizza, username — mai una
  password), istruzioni testuali ("cosa fare": chiudere l'account, contattare l'assicurazione,
  trasferire, scaricare i dati prima, ecc.)
- Designazione beneficiari + relazione, invariato
- Trigger di inattività (differenziatore reale rispetto ad Apple, che richiede un certificato di
  morte) → invia solo istruzioni, mai credenziali
- Elimina quasi del tutto l'esposizione penale (11.3) e il rischio di data breach, perché non c'è
  nulla di sensibile da rubare

**Modulo avanzato (fase successiva, opzionale, eventualmente a pagamento) — "Vault sicuro"**
- Reintroduce lo storage di credenziali, ma con cifratura **zero-knowledge client-side** — il
  server non vede mai né chiave né testo in chiaro
- Investimento ingegneristico non banale: solo dopo che il modulo core è validato con utenti reali
- Alternativa più economica e più veloce da mettere sul mercato: non ricostruire un vault
  proprietario, integrarsi o rimandare a password manager esistenti con emergency access già
  collaudato (1Password, Proton Pass)

**Modulo verifica identità (futuro)** — OTP email o SPID per confermare l'identità del beneficiario
prima di rilasciare le istruzioni.

### 12.4 — Ampliamento oltre gli "asset digitali": conti, assicurazioni, accessi ad app

Il modello dati attuale (`DigitalAsset.asset_type`) ha già un campo `financial` e `subscription`,
quindi l'estensione non richiede un nuovo schema, solo nuove categorie e un cambio di
posizionamento:

| Categoria nuova/estesa | Esempio di voce | Cosa serve (senza credenziali) |
|---|---|---|
| Conto corrente/deposito | Banca, IBAN, filiale di riferimento | Istruzioni: chi contattare, dove sono i documenti cartacei |
| Polizza assicurativa (vita, casa, RC) | Compagnia, numero polizza | Contatto agente/compagnia, beneficiario già designato in polizza o da coordinare |
| Utenze e abbonamenti | Luce, gas, Netflix, palestra | Istruzioni: disdire, trasferire intestazione |
| Accessi ad app professionali/gestionali | Gestionale studio, CRM, cloud aziendale | Istruzioni: chi in azienda ha già accesso admin, a chi rivolgersi |
| Documenti legali collegati | Testamento, procura, mandato post-mortem | Dove si trova l'originale, chi lo custodisce (notaio) |

Questo non è "aggiungere feature": è riconoscere che, una volta tolte le password dal core, il
prodotto smette di essere un "vault per account digitali" e diventa un **indice generale del
patrimonio + degli accessi + delle istruzioni** — categoria più vicina a Everplans (Sezione 4.1)
che ai soli Apple/Google Legacy Contact. Ha un vantaggio concreto per il Modello B: un notaio o un
commercialista può usarlo per l'intera pratica successoria, non solo per la parte "social/crypto",
il che aumenta la willingness-to-pay e il valore percepito per studio.

**Attenzione**: allargare lo scope a conti e polizze aumenta anche l'ambiguità legale — un conto
corrente rientra già nell'asse ereditario "classico" con procedure consolidate (non serve
inventarlo su un'app terza per la parte legale, che passa comunque da dichiarazione di successione
notarile). Il valore aggiunto reale di Digital Legacy qui non è sostituire la successione legale,
ma **essere l'indice che dice ai familiari dove guardare** — un "cosa esiste e chi contattare",
non un sostituto della dichiarazione di successione. Va comunicato chiaramente per evitare che il
prodotto sembri promettere una funzione legale che non ha.

### 12.5 — Posizionamento per il target 50-60enne: "mappa di famiglia", non "vault di sicurezza"

Il modulo core disegnato in 12.1-12.4 risolve un problema tecnico/legale (niente credenziali in
giro). Ma c'è anche un problema di posizionamento che vale la pena affrontare esplicitamente,
perché cambia sia il messaggio sia — in parte — il prodotto: **il 50-60enne di oggi non è
digital native**. Ha 20-30 anni di sedimentazione digitale (email, home banking, social,
abbonamenti) accumulata senza un criterio, ma il suo problema reale non è la sicurezza
informatica — è la stessa ansia che ha per il cassetto dei documenti cartacei: *"se mi succede
qualcosa, i miei figli sapranno dove guardare?"*

**Perché il framing "indice", non "vault", è quello giusto per questo target**
Un vault di credenziali risponde a un'ansia di sicurezza (furto, breach) più sentita da un target
giovane/crypto-native. Per il target 50-60 l'ansia è organizzativa, non di sicurezza. "L'indice
che dice dove guardare" ricalca un modello mentale che questa generazione già possiede — il
notaio, il faldone, "chiedi a tuo zio dov'è il testamento" — invece di chiederle di fidarsi di un
concetto (vault cifrato zero-knowledge) che non ha gli strumenti per valutare, e che
intuitivamente non applica nemmeno alle proprie password quotidiane (la maggioranza le scrive su
un foglio, non usa un password manager). Questo abbassa in modo diretto la barriera di fiducia
individuata come rischio più grande dell'intero piano (Sezione 6, Rischio 1): è molto più facile
scrivere "ho una polizza vita con Generali, referente il mio commercialista" che scrivere la
password vera.

**L'estensione di prodotto che ne consegue: utile anche in vita, non solo post-mortem**
Se il messaggio diventa "aiuto chi resta a trovare tutto" invece di "gestione patrimonio
digitale", si apre un caso d'uso più grande e più urgente di quello attuale: la cura dei genitori
anziani mentre sono ancora vivi. Il 50-60enne di oggi è spesso generazione sandwich — gestisce già
oggi le pratiche dei genitori 80-90enni, non solo la propria eventuale successione. "Mamma è
appena stata ricoverata e non troviamo il numero della sua assicurazione" è uno scenario che
capita molto più spesso della morte, e non richiede alcun trigger di inattività per generare
valore: la mappa serve da subito, condivisa e aggiornata in famiglia, non sbloccata solo al
decesso. Questo riduce anche, come effetto collaterale, il problema dei falsi positivi del dead
man's switch (11.4): il prodotto non dipende più esclusivamente dall'inferire correttamente la
morte per essere utile.

**Implicazione per il canale B2B notai**
Un "vault di credenziali" è un prodotto con responsabilità e rischio percepito alto da consigliare
a un cliente. Un "indice/checklist da compilare insieme al cliente" è invece uno strumento che
notaio o commercialista possono proporre senza esporsi — complemento al testamento, non sistema
che maneggia segreti. Più facile da vendere, più coerente con 12.4.

**Due tensioni da tenere sotto controllo**
1. *Verticale crypto (Modello C)*: per una chiave privata/seed phrase persa non esiste "chi
   contattare" — non c'è un servizio clienti da chiamare. Il framing "indice, non vault" non copre
   questo caso: va comunicato come eccezione esplicita, non come estensione naturale del core.
2. *Rischio di sovra-promettere*: "indice che dice dove guardare" deve restare esplicitamente
   *non* un sostituto della dichiarazione di successione (coerente con l'avvertenza già in 12.4) —
   il claim corretto è "riduce il tempo e l'ansia di cercare", non "risolve la successione".

**Raccomandazione**: orientare comunicazione e onboarding su "mappa di famiglia, utile da subito,
non solo dopo" come messaggio principale — non "gestione sicura del patrimonio digitale" — con il
disclaimer legale come nota secondaria, non come titolo. In pratica: il tono del prodotto si
avvicina più a "organizzazione familiare" che a "sicurezza informatica".

### Perché questa non è (solo) una scelta tecnica, ma la risposta giusta alla critica di mercato
Uno dei punti più duri della critica esterna era: "il prodotto non aggiunge valore rispetto ad
Apple/Google gratis". Se la differenziazione cercata fosse stata "un vault di credenziali più
sicuro", quella critica avrebbe ragione — è un terreno dove Big Tech e i password manager sono già
forti. Spostando la differenziazione su **copertura multi-piattaforma e multi-categoria** (crypto,
conti, polizze, servizi italiani, tutto ciò che non è Apple/Google), **trigger di inattività**
(assente in Apple, che richiede certificato di morte) e **completezza dell'indice + istruzioni**,
il prodotto core diventa più semplice, più sicuro per costruzione, copre un problema più ampio di
quello di Apple, e la sua proposta di valore non dipende più dal competere su sicurezza dei dati
con chi ha risorse enormemente superiori.

### Conclusione sul pivot
Non è un pivot di business: il target (notai/studi legali, o in alternativa il verticale crypto)
resta valido, così come il Modello B come priorità. Cambia **cosa si costruisce per primo e quanto
è ampio**: si rimanda la feature a più alto rischio/costo (vault di credenziali) — che oltretutto
non è mai stata essenziale al flusso reale del prodotto — a un modulo opzionale futuro, si porta a
MVP la versione più semplice e legalmente più difendibile, e la si allarga da "asset digitali" a
"indice generale del patrimonio e degli accessi", che è più vicino a ciò che un notaio o un
familiare cerca davvero in un momento di successione.

### 12.6 — Permessi granulari per contatto e distinzione contatto/erede legale

Il modello binario "condiviso da subito" vs "segreto fino alla morte" (12.5) va raffinato: per
ogni contatto designato, il titolare deve poter scegliere **cosa** condividere e **quando**, non
solo se condividere.

**Matrice permessi (chi, cosa, quando)**
- *Chi*: quale contatto (già modellato in `Beneficiary`)
- *Cosa*: istruzioni, riferimenti pubblici, eventuali contenuti propri del titolare (foto, mail —
  fuori scope MVP, solo se il prodotto evolve in quella direzione), vault avanzato (password)
- *Quando*: accesso live (da subito) oppure solo al trigger post-mortem

Estensione naturale del modello dati esistente: `AssetAssignment` è già la relazione N:N
asset↔beneficiario con istruzioni per-coppia. Basta aggiungere un campo `access_timing` (live /
solo-trigger) e uno scope di contenuto, senza introdurre un nuovo schema.

**Distinzione critica: "contatto con accesso" ≠ "erede legale"**
In Italia chi eredita è determinato dal testamento o dalla successione legittima (artt. 565 e ss.
c.c.), mai da una designazione fatta su un'app terza. Questo va reso esplicito, per due motivi:
1. **Evitare aspettative false**: se l'utente crede di poter "distribuire l'eredità" tramite
   l'app, e il contatto designato non coincide con l'erede legale reale, il prodotto ha
   contribuito a generare un conflitto familiare.
2. **Protezione del prodotto**: se un erede legale escluso contestasse l'accesso dato a un
   non-erede, l'app deve poter dimostrare di aver sempre trattato "contatto designato" come ruolo
   puramente operativo (chi riceve informazioni), mai come attribuzione di diritti.

Implicazione tecnica: il campo `relationship` già esistente (spouse, child, ecc.) resta
informativo, non va mai trasformato in un campo tipo "erede legale" — l'app non deve arrogarsi una
determinazione che non le compete. Serve invece un disclaimer esplicito in UI e T&C.

**Correzione alla matrice di rischio (11.3 / 12)**
Il rischio penale (Art. 615-ter) non dipende dal *quando* (vivo vs morto) ma dal *cosa*: contenuti
propri del titolare condivisi in vita con consenso esplicito (foto, mail, istruzioni) non
comportano alcun rischio — è condivisione autorizzata, come un album condiviso. Il rischio resta
concentrato solo sulle credenziali che permettono di accedere a sistemi di terzi, in vita o
post-mortem, perché quell'account non è "proprietà" del titolare da poter condividere liberamente.
Questo isola ulteriormente il vault di credenziali come unica area che giustifica l'architettura
zero-knowledge separata (Fase 3), indipendentemente dalla granularità dei permessi.

**Nota architetturale**: l'accesso "live" richiede che il beneficiario diventi un utente
autenticato (oggi `Beneficiary` è solo un destinatario passivo di email, senza login). È un
cambiamento reale, non enorme ma non banale: un secondo tipo di account con permessi scoped per
asset/categoria, non solo un indirizzo email di destinazione. Va preventivato nella Fase 1/2 della
roadmap se si vuole realizzare l'accesso live descritto in 12.5.

### 12.7 — Può funzionare come business? Analisi critica e realistica

**Verdetto diretto**: come business a scala, probabilmente no. Come piccola attività B2B
redditizia gestita con pazienza, è plausibile — ma il rischio di esecuzione si concentra quasi
interamente in un solo punto: la vendita a un canale (notai) strutturalmente lento e diffidente
verso il software esterno.

**Non è un business scalabile.** Il TAM corretto (~5.000 notai) pone un tetto strutturale: anche
il 10% di penetrazione all'anno 3 vale ~€500K ARR (Sezione 8) — un buon risultato per un'attività
solista o a due persone, non per una startup che giustifichi investimento o crescita di team.
Allargare a commercialisti/consulenti patrimoniali aiuta ma non cambia l'ordine di grandezza:
resta un mercato di nicchia professionale italiana, non un mercato scalabile globalmente.

**Il canale B2B notai costa più di quanto l'unit economics attuale assuma.** Il piano stima
margine >90% e costi infra ~€100/mese (Sezione 8), coerente con un motore self-serve/PLG a basso
CAC. Ma vendere a notai — categoria lenta nell'adozione tecnologica, relazionale, sensibile alla
responsabilità professionale — richiede quasi certamente vendita diretta e relazionale (fiere di
settore, contatti personali, referral tra studi), non acquisizione via web. Questo implica costi
di go-to-market più alti di quelli previsti e cicli di vendita lunghi (mesi, non settimane) prima
di vedere ricavi — un fattore che l'unit economics in Sezione 8 non riflette.

**Il rischio esistenziale già segnalato in 11.6 è concreto, non teorico.** Se il Notariato
standardizza il protocollo con Microsoft e Google, un prodotto terzo rischia di essere bypassato
proprio nel canale su cui il piano punta tutto — un ente che lavora già in quella direzione con
partner dalle risorse enormemente superiori.

**Il posizionamento "mappa di famiglia, utile in vita" (12.5) migliora l'engagement ma non è
privo di precedenti fallimentari.** Gli strumenti di organizzazione della vita/famiglia
(raccoglitori documenti, planner condivisi) hanno storicamente ritenzione ed engagement bassi: le
persone intendono organizzarsi ma procrastinano — lo stesso problema del 13% di tasso testamentario
già citato in 4.3. Rendere il prodotto utile "anche in vita" riduce il rischio di app-zombie
(installata e mai più aperta), ma introduce più superficie da costruire (autenticazione
beneficiario, permessi granulari, notifiche — vedi 12.6) per un team presumibilmente piccolo.

**Il prodotto ha un problema strutturale da "polizza assicurativa".** Il suo valore si manifesta
una sola volta, in un momento imprevedibile, dopo mesi o anni di uso quasi nullo. Se in quel
momento fallisce — trigger che non scatta, email non recapitata, beneficiario che non riceve
nulla — il danno reputazionale per un brand piccolo e senza sponsor istituzionale è potenzialmente
fatale, mentre Apple e Google hanno riserve di fiducia che assorbono singoli fallimenti.

**Conclusione onesta**: la strada più realistica non è "startup scalabile" ma "piccola attività di
nicchia B2B, sostenibile se il fondatore ha accesso diretto e pazienza per il canale
notarile/commercialisti" — oppure, più concretamente, un prodotto costruito come leva per una
partnership o acquisizione da parte di un attore più grande (assicurazione, banca, o lo stesso
Notariato — Modello D) piuttosto che come azienda indipendente a lungo termine.
