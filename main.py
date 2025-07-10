import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from datetime import datetime, timedelta
import asyncio

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("❌ BOT_TOKEN não definido nas variáveis de ambiente!")
ARQUIVO = "mensagem.txt"

async def handle_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        with open(ARQUIVO, "r", encoding="utf-8") as f:
            linhas = [l.strip() for l in f if l.strip()]
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Erro ao ler arquivo: {e}")
        return

    texto_recebido = update.message.text.strip()

    for linha in linhas:
        if not linha.startswith("/"):
            continue

        partes = linha.split(";", maxsplit=1)
        if len(partes) != 2:
            continue

        comando, conteudo = partes
        if texto_recebido == comando.strip():
            dados = conteudo.split(";")
            cred = {
                "sistema": dados[0].strip() if len(dados) > 0 else "-",
                "usuario": dados[1].strip() if len(dados) > 1 else "-",
                "senha": dados[2].strip() if len(dados) > 2 else "-",
                "host": dados[3].strip() if len(dados) > 3 else "-",
                "porta": dados[4].strip() if len(dados) > 4 else "-",
            }

            msg = (
                f"✅ Acesso autorizado!\n\n"
                f"🔧 *Sistema:* {cred['sistema']}\n"
                f"👤 *Usuário:* {cred['usuario']}\n"
                f"🔑 *Senha:* {cred['senha']}\n"
                f"📡 *Host:* {cred['host']}\n"
                f"📍 *Porta:* {cred['porta']}"
            )

            sent = await context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode="Markdown")
            await asyncio.sleep(120)
            await sent.delete()
            return

    await context.bot.send_message(chat_id=update.effective_chat.id, text="❌ Comando não encontrado.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Olá! Envie um comando para receber as credenciais!")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    # Handler fixo para /start
    app.add_handler(CommandHandler("start", start))

    # Handler para qualquer outro comando (ex: /acesso)
    app.add_handler(MessageHandler(filters.COMMAND, handle_command))

    print("Bot rodando...")
    app.run_polling()

