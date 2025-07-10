import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler,
    filters, ContextTypes
)
import asyncio

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("❌ BOT_TOKEN não definido!")

ARQUIVO = "mensagem.txt"
SENHA_CORRETA = "potiguar123"
PORTA = int(os.getenv("PORT", 8080))

usuario_em_espera = {}  # user_id -> módulo escolhido

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("EPORTAL", callback_data="EPORTAL")],
        [InlineKeyboardButton("PRP", callback_data="PRP")],
        [InlineKeyboardButton("AUTH", callback_data="AUTH")],
        [InlineKeyboardButton("MCS_EPORTAL", callback_data="MCS_EPORTAL")]
    ]
    await update.message.reply_text("Selecione o módulo:", reply_markup=InlineKeyboardMarkup(keyboard))

async def ao_clicar_modulo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    modulo = query.data
    user_id = query.from_user.id
    usuario_em_espera[user_id] = modulo

    await query.message.reply_text(f"🔒 Digite a senha para acessar o módulo *{modulo}*:", parse_mode="Markdown")

async def ao_receber_mensagem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    senha = update.message.text.strip()

    if user_id not in usuario_em_espera:
        await update.message.reply_text("Use /start para iniciar.")
        return

    modulo = usuario_em_espera[user_id]

    if senha != SENHA_CORRETA:
        await update.message.reply_text("❌ Senha incorreta.")
        del usuario_em_espera[user_id]
        return

    try:
        with open(ARQUIVO, "r", encoding="utf-8") as f:
            linhas = [l.strip() for l in f if l.startswith("/") and modulo.upper() in l]
    except Exception as e:
        await update.message.reply_text(f"Erro ao ler o arquivo: {e}")
        return

    if not linhas:
        await update.message.reply_text("❌ Módulo não encontrado.")
        return

    comando, conteudo = linhas[0].split(";", maxsplit=1)
    dados = conteudo.split(";")

    cred = {
        "sistema": dados[0].strip() if len(dados) > 0 else "-",
        "usuario": dados[1].strip() if len(dados) > 1 else "-",
        "senha": dados[2].strip() if len(dados) > 2 else "-",
        "host": dados[3].strip() if len(dados) > 3 else "-",
        "porta": dados[4].strip() if len(dados) > 4 else "-"
    }

    msg = (
        f"✅ Acesso autorizado!\n\n"
        f"🔧 *Sistema:* {cred['sistema']}\n"
        f"👤 *Usuário:* {cred['usuario']}\n"
        f"🔑 *Senha:* {cred['senha']}\n"
        f"📡 *Host:* {cred['host']}\n"
        f"📍 *Porta:* {cred['porta']}"
    )

    sent = await update.message.reply_text(msg, parse_mode="Markdown")
    await asyncio.sleep(120)
    await sent.delete()
    del usuario_em_espera[user_id]

# --- Execução via Webhook ---
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(ao_clicar_modulo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ao_receber_mensagem))

    print("Bot rodando com Webhook...")

    app.run_webhook(
        listen="0.0.0.0",
        port=PORTA,
        webhook_url=f"https://potiguar-bot.onrender.com"  # troque pelo seu domínio
    )

