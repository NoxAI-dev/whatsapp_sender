WhatsApp Sender – Instruções Rápidas (PT-BR)

1) Conteúdo deste pacote
   - send_whatsapp.exe
   - .env
   - chrome_profile/          (mantém a sessão do WhatsApp Web)
   - README.txt

2) Pré-requisitos
   - Google Chrome instalado.
   - A planilha Google Sheets compartilhada (qualquer pessoa com o link – Leitor).
   - O .env preenchido com o link de exportação CSV da aba correta (ver item 4).

3) Primeira execução
   - Dê duplo-clique em send_whatsapp.exe.
   - O Chrome abrirá em web.whatsapp.com.
   - Escaneie o QR Code com o aplicativo do WhatsApp (apenas na primeira vez).
   - Aguarde o envio automático.

4) Configurar o .env
   SHEET_CSV_URL=https://docs.google.com/spreadsheets/d/<ID>/export?format=csv&gid=<GID>
   DELAY_BETWEEN=20
   TIMEOUT_OPEN=50
   HEADLESS=false
   SEND_ONLY_IF_OVERDUE=true

   Observações:
   - SEND_ONLY_IF_OVERDUE=true → envia apenas se "dias em atraso" >= 1.
   - Se estiver testando e não tiver atrasados, mude temporariamente para false.

5) Estrutura esperada da planilha (colunas)
   nome | cpf | Telefone | vencimento | dias em atraso | mensagem | link_wa_formula | Enviar
   - O cálculo de "dias em atraso", a "mensagem", o "link_wa_formula" e o botão "Enviar" são preenchidos pelo Apps Script (sem fórmulas nas células).
   - Telefone: só dígitos (DDI+DDD+número).

6) Uso diário
   - Dê duplo-clique em send_whatsapp.exe.
   - Não feche a janela até o término.
   - O histórico é salvo em registro_de_envios.csv (acréscimo/append).

7) Problemas comuns
   - Não envia nada: verifique se há linhas com "dias em atraso" >= 1 (ou defina SEND_ONLY_IF_OVERDUE=false).
   - Pede QR toda vez: não apague a pasta chrome_profile/.
   - Conversa abre mas não envia: aumente TIMEOUT_OPEN (ex.: 60) e mantenha DELAY_BETWEEN >= 12.

8) Suporte
_________________________________________

📞 Suporte e Contato  
Desenvolvedor: NoxAI  
✉️ Email: noxai.dev@gmail.com  
💬 Github: NoxAI-dev  
🌐 Documentação: https://link-para-docs
_________________________________________
