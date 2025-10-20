# Setup Completato - QCoder CLI

## ✅ Configurazione Completata

Il tuo file `.env` è stato creato con la tua API key OpenRouter. Il file è protetto e **non verrà mai committato** su GitHub (è nel `.gitignore`).

## 🚀 Prossimi Passi

### 1. Installa QCoder

Apri il terminale nella directory del progetto e esegui:

```bash
pip install -r requirements.txt
pip install -e .
```

### 2. Verifica l'Installazione

```bash
# Controlla la versione
qcoder --version

# Dovrebbe mostrare: QCoder CLI v0.1.0
```

### 3. Test Rapido

Prova questi comandi per verificare che tutto funzioni:

```bash
# Fai una domanda veloce
qcoder ask "Che cos'è Python?"

# Avvia chat interattiva
qcoder chat
```

Nella chat interattiva, prova:
- "Ciao, come funzioni?"
- "Spiegami cosa sono le list comprehension in Python"
- "/help" per vedere i comandi
- "/exit" per uscire

### 4. Inizializza un Progetto

```bash
# Vai in una directory del tuo progetto
cd /path/to/your/project

# Inizializza QCoder
qcoder init

# Questo crea:
# - .qcoder/config.yaml
# - .qcoder/QCODER.md
```

Poi personalizza `.qcoder/QCODER.md` con informazioni sul tuo progetto.

## 📋 Comandi Disponibili

### Chat e Domande

```bash
# Chat interattiva
qcoder chat
qcoder chat --resume nome_sessione
qcoder chat --model qwen/qwen3-coder:free

# Domanda singola
qcoder ask "Come funziona async/await in Python?"
qcoder ask "Spiega questo errore" --output spiegazione.txt
```

### Operazioni su File

```bash
# Analizza file
qcoder file main.py --prompt "Spiega questo codice"

# Trova pattern
qcoder file . --prompt "Trova tutti i TODO nel progetto"

# Trasforma codice
qcoder file script.py --prompt "Aggiungi docstring" --output migliorato.py
```

### Comandi Shell

```bash
# Esegui comando
qcoder shell ls -la

# Spiega comando prima di eseguirlo
qcoder shell --explain "git rebase -i HEAD~3"

# Auto-approva esecuzione
qcoder shell npm install -y
```

### GitHub (richiede gh CLI)

```bash
# Review PR
qcoder github --pr 123

# Analizza issue
qcoder github --issue 456

# Crea PR con descrizione AI
qcoder github --create-pr
```

### Gestione Conversazioni

```bash
# Lista conversazioni salvate
qcoder conversations

# Riprendi conversazione
qcoder chat --resume nome_conversazione
```

### Configurazione

```bash
# Mostra config
qcoder config
qcoder config --global

# Imposta valori
qcoder config --set model=qwen/qwen3-coder:free
qcoder config --set max_context_length=16000
```

## 🔧 Risoluzione Problemi

### "Command not found: qcoder"

```bash
# Reinstalla
pip install -e .

# Verifica PATH
which qcoder  # Linux/Mac
where qcoder  # Windows
```

### Errori di Import

```bash
# Assicurati di essere nella directory corretta
cd C:\Users\chatg\Documents\GitHub\QcoderCLI

# Reinstalla dipendenze
pip install -r requirements.txt
pip install -e .
```

### API Key Non Trovata

Verifica che il file `.env` esista e contenga:
```
OPENROUTER_API_KEY=sk-or-v1-...
```

## 📦 Commit su GitHub

Quando sei pronto per committare:

```bash
# Aggiungi tutti i file (esclude .env automaticamente)
git add .

# Commit
git commit -m "feat: initial QCoder CLI implementation

- Interactive AI chat with Qwen3-Coder
- File operations and code analysis
- Shell command execution with AI
- GitHub integration (PR review, issue triage)
- Web search grounding with DuckDuckGo
- Plugin system and MCP server
- Workflow automation
- Complete documentation"

# Push
git push origin main
```

Il file `.env` con la tua API key **NON verrà mai committato** perché è nel `.gitignore`.

## 🎯 Funzionalità Principali

- ✅ **Chat AI Interattiva** - Conversazioni nel terminale
- ✅ **Analisi Codice** - Spiega e trasforma codice
- ✅ **Shell Integration** - Esegui comandi con assistenza AI
- ✅ **GitHub** - Review PR, analisi issue
- ✅ **Web Search** - Informazioni aggiornate via DuckDuckGo
- ✅ **Plugin System** - Estendi funzionalità
- ✅ **Checkpoint** - Salva/riprendi conversazioni
- ✅ **Context Files** - QCODER.md per contesto progetto
- ✅ **Workflow** - Automazione task con YAML

## 📚 Documentazione

- **README.md** - Documentazione completa
- **QUICKSTART.md** - Guida rapida (5 minuti)
- **INSTALLATION.md** - Installazione dettagliata
- **CONTRIBUTING.md** - Come contribuire
- **PROJECT_SUMMARY.md** - Riepilogo tecnico

## 🔐 Sicurezza

- ✅ API key protetta (non committata)
- ✅ Rilevamento comandi pericolosi
- ✅ Validazione input
- ✅ Logging sicuro

## 🆓 Modello AI Gratuito

QCoder usa **Qwen3-Coder** via OpenRouter:
- ✅ Completamente gratuito
- ✅ Ottimizzato per coding
- ✅ Supporto multimodale
- ✅ Nessun limite rate (tier free)

## 🎉 Pronto all'Uso!

Il tuo QCoder CLI è completamente configurato e pronto all'uso. Divertiti a programmare con l'assistenza AI! 🚀

---

**Hai domande?** Controlla la documentazione o apri un issue su GitHub.
