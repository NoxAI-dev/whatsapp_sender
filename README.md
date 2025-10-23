<h1 align="center">🕯️ WhatsApp Sender</h1>

<p align="center">
Automação de cobranças via WhatsApp com integração ao Google Sheets e envio inteligente por régua de atraso.
<br>
Desenvolvido por <a href="https://github.com/NoxAI-dev">NoxAI</a> ⚙️
</p>

---

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Selenium-Automation-success?logo=selenium&logoColor=white" alt="Selenium">
  <img src="https://img.shields.io/badge/Build-PyInstaller-orange?logo=windows&logoColor=white" alt="Build">
  <img src="https://img.shields.io/badge/Platform-Windows-lightgrey?logo=windows" alt="Windows">
  <img src="https://img.shields.io/badge/Status-Em%20Desenvolvimento-purple" alt="Status">
</p>

---

## ⚙️ Funcionalidades

✅ Geração automática de mensagens de cobrança personalizadas  
✅ Envio automatizado via WhatsApp Web (Selenium + ChromeDriver)  
✅ Registro de envios e falhas em CSV  
✅ Integração com Google Sheets (via export CSV)  
✅ Build automatizado para Windows com PyInstaller  

---

## 🧩 Estrutura do Projeto

📦 whatsapp_sender/
┣ 📂 build/ # Build temporário
┣ 📂 dist/ # Executável final (.exe)
┣ 📂 release/ # Versões empacotadas
┣ 📂 chrome_profile/ # Perfil do Chrome com login do WhatsApp
┣ 📜 send_whatsapp.py # Código principal
┣ 📜 send_whatsapp.spec # Configuração PyInstaller
┣ 📜 requirements-win.txt # Dependências
┣ 📜 build_win.bat # Script automatizado de build
┣ 📜 registro_de_envios.csv # Log de mensagens enviadas
┣ 📜 .env # Variáveis de ambiente
┣ 📜 .gitignore
┗ 📜 README.md

yaml
Copiar código

---

## 💻 Instalação

```bash
git clone https://github.com/NoxAI-dev/whatsapp_sender.git
cd whatsapp_sender
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-win.txt
⚡ Geração do Executável
bash
Copiar código
.\build_win.bat
O executável será gerado em:

Copiar código
dist\whatsapp_sender\whatsapp_sender.exe
🔐 Configuração (.env)
env
Copiar código
SHEET_CSV_URL=https://docs.google.com/spreadsheets/...
CSV_PATH=
DELAY_BETWEEN=10
TIMEOUT_OPEN=25
HEADLESS=false
SEND_ONLY_IF_OVERDUE=true
🧠 Fluxo de Funcionamento
1️⃣ Leitura do CSV exportado do Google Sheets
2️⃣ Cálculo automático dos dias em atraso
3️⃣ Geração da mensagem personalizada
4️⃣ Abertura do WhatsApp Web via Selenium
5️⃣ Envio e registro no registro_de_envios.csv

🧑‍💻 Desenvolvido por
👤 NoxAI
📧 noxai.dev@gmail.com
🌐 github.com/NoxAI-dev

🛠️ Tecnologias Utilizadas
Python 3.10+

Selenium WebDriver

Pandas

dotenv

PyInstaller

🔮 Roadmap
 Implementar régua inteligente (1–10, 10–20, 30+ dias)

 Suporte a múltiplos perfis do Chrome

 Relatórios visuais em dashboard

 Integração com Google Drive / Sheets em tempo real

⚖️ Licença
Distribuído sob a licença MIT.
© 2025 NoxAI – Todos os direitos reservados.

<h4 align="center">🖤 Criado por NoxAI • Pela Vontade da Noite ⚔️</h4> ```