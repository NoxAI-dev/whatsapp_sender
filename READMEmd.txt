# ⚙️ WhatsApp Sender – Automação de Cobranças

Automação completa de **envio de mensagens de cobrança via WhatsApp**, usando **Google Sheets + Python + Selenium**.  
Projeto desenvolvido por **NoxAI**.

---

## 🧩 Estrutura do Projeto

whatsapp_sender/
├─ .env
├─ send_whatsapp.py
├─ build_win.bat
├─ requirements-win.txt
├─ registro_de_envios.csv
├─ dist/
│ └─ whatsapp_sender.exe
└─ chrome_profile/

yaml
Copiar código

---

## 🚀 Funcionalidades

- Lê automaticamente dados da planilha do Google Sheets exportada em CSV.
- Calcula dias em atraso e monta mensagem personalizada (via Apps Script).
- Envia mensagens automaticamente via **WhatsApp Web (Selenium)**.
- Cria logs de todos os envios (`registro_de_envios.csv`).
- Permite compilar executável standalone via **PyInstaller**.

---

## 🧮 Fluxo de Automação

1️⃣ **Google Sheets + Apps Script**
   - Gera automaticamente as mensagens de cobrança.
   - Calcula os dias de atraso.
   - Cria os links `wa.me` e botão de envio manual.

2️⃣ **Python / Executável**
   - Faz leitura do CSV exportado da planilha.
   - Filtra clientes com atraso (`dias_em_atraso >= 1`).
   - Automatiza login no WhatsApp Web e envio das mensagens.

---

## ⚙️ Configuração do `.env`

| Variável | Descrição | Exemplo |
|-----------|------------|----------|
| `SHEET_CSV_URL` | URL de exportação CSV da planilha do Google Sheets | `https://docs.google.com/spreadsheets/d/.../export?format=csv&gid=...` |
| `DELAY_BETWEEN` | Delay entre envios (em segundos) | `20` |
| `TIMEOUT_OPEN` | Tempo máximo de espera para abrir conversa (s) | `50` |
| `HEADLESS` | Se `true`, executa sem abrir navegador | `false` |
| `SEND_ONLY_IF_OVERDUE` | Envia só se tiver atraso | `true` |

---

## 🧰 Dependências

Todas as dependências estão listadas no arquivo:

requirements-win.txt

go
Copiar código

Para instalar manualmente:
```bash
pip install -r requirements-win.txt
🧱 Build do Executável
Gerar um executável .exe com PyInstaller:

bash
Copiar código
.\build_win.bat
O executável será criado em:

Copiar código
dist\whatsapp_sender\whatsapp_sender.exe
📜 Logs
Os logs de envio ficam registrados em:

Copiar código
registro_de_envios.csv
Com as colunas:

lua
Copiar código
timestamp | nome | telefone | dias_em_atraso | status | detalhe | msg_hash
🧑‍💻 Autor
Desenvolvido por NoxAI

Automação, IA e Branding Pessoal
github.com/noxai-dev