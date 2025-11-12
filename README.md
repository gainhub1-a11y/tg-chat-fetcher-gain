# 🪄 TG Chat Fetcher Gain

**TG Chat Fetcher Gain** è un microservizio basato su **FastAPI + Telethon** che permette di scaricare file e media da Telegram (video, foto, documenti, ecc.) **senza limiti di 20 MB**, utilizzando il protocollo **MTProto** tramite la tua sessione utente (`STRING_SESSION`).

È compatibile con:
- ✅ **Canali e supergruppi**
- ✅ **Chat private con bot o utenti**
- ✅ Integrazioni **Make.com**, **n8n** o qualsiasi flusso HTTP

---

## 🚀 Funzionalità principali

| Tipo | Descrizione |
|------|--------------|
| 🔹 `/health` | Verifica se il client Telegram è connesso correttamente |
| 🔹 `/resolve` | Risolve un `chat_id` o un `peer` (username) e restituisce info sul canale/chat |
| 🔹 `/download` | Scarica un file/media da un messaggio Telegram e restituisce il binario |

---

## ⚙️ Setup su Render

### 1️⃣ Variabili d’ambiente obbligatorie

| Nome | Descrizione |
|------|--------------|
| `API_ID` | ID numerico di Telegram (da [my.telegram.org](https://my.telegram.org)) |
| `API_HASH` | Hash di Telegram |
| `STRING_SESSION` | Stringa generata con Telethon (puoi crearla da Google Colab) |

**Facoltativo:**
| Nome | Descrizione |
|------|--------------|
| `API_KEY` | Chiave opzionale per proteggere l’API (`X-API-Key` header) |

---

### 2️⃣ Comandi di avvio

**Build command**
```bash
pip install -r requirements.txt
