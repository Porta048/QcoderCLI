# 🚀 Inizia da Qui - QCoder CLI

## Installazione Rapida (3 Passi)

### 1️⃣ Installa Dipendenze

```bash
pip install -r requirements.txt
```

### 2️⃣ Installa QCoder

```bash
pip install -e .
```

### 3️⃣ Testa

```bash
qcoder ask "Ciao! Come funzioni?"
```

✅ Se vedi una risposta dell'AI, tutto funziona!

---

## 🎯 Comandi Essenziali

### Chat Interattiva

```bash
qcoder chat
```

Comandi nella chat:
- `/help` - Aiuto
- `/save` - Salva conversazione
- `/clear` - Pulisci cronologia
- `/exit` - Esci

### Domanda Veloce

```bash
qcoder ask "Come leggere un file in Python?"
```

### Analizza File

```bash
qcoder file main.py --prompt "Spiega questo codice"
```

### Esegui Comando Shell

```bash
qcoder shell --explain "git status"
```

---

## 📖 Documentazione Completa

- **SETUP_COMPLETATO.md** - Guida completa setup
- **README.md** - Tutte le funzionalità
- **QUICKSTART.md** - Tutorial 5 minuti

---

## ❓ Problemi?

### "Command not found"

```bash
pip install -e .
```

### Errore API Key

Il file `.env` è già configurato. Se hai problemi:

```bash
cat .env  # Verifica che esista
```

---

## 🎉 Pronto!

Inizia con:

```bash
qcoder chat
```

E chatta con l'AI! 🤖
