import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)
import asyncio

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("❌ BOT_TOKEN não definido!")

SENHA_CORRETA = "potiguar123"
PORTA = int(os.getenv("PORT", 8080))

# Armazena o módulo selecionado por cada usuário
usuario_modulo = {}

DADOS_FIXOS = {
    "EPORTAL": {
        "sistema": "EPORTAL",
        "usuario": "TESTE",
        "senha": "123",
        "host": "192.5.5.5",
        "porta": "1515"
    },
    "AUTH": {
        "sistema": "AUTH",
        "usuario": "TESTE AUTH",
        "senha": "12345",
        "host": "192.0.0.5",
        "porta": "1515"
    },
    "PRP": {
        "sistema": "PRP",
        "usuario": "TESTE PRP",
        "senha": "senhaPRP",
        "host": "192.168.1.1",
        "porta": "3306"
    },
    "MCS_EPORTAL": {
        "sistema": "MCS_EPORTAL",
        "usuario": "MCS_USER",
        "senha": "mcs123",
        "host": "10.0.0.10",
        "porta": "5432"
    }
}

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("👉 EPORTAL", callback_data="EPORTAL")],
        [InlineKeyboardButton("👉 PRP", callback_data="PRP")],
        [InlineKeyboardButton("👉 AUTH", callback_data="AUTH")],
        [InlineKeyboardButton("👉 MCS_EPORTAL", callback_data="MCS_EPORTAL")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Escolha um dos módulos abaixo:", reply_markup=reply_markup)

# Quando clicar num botão
async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    modulo = query.data
    user_id = query.from_user.id
    usuario_modulo[user_id] = modulo
    await query.message.reply_text(f"🔒 Digite a senha para acessar o módulo {modulo}:")

# Quando mandar a senha
async def ao_receber_texto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    texto = update.message.text.strip()

    if user_id not in usuario_modulo:
        await update.message.reply_text("❗ Use /start e selecione um módulo primeiro.")
        return

    if texto != SENHA_CORRETA:
        await update.message.reply_text("❌ Senha incorreta.")
        del usuario_modulo[user_id]
        return

    modulo = usuario_modulo[user_id]
    dados = DADOS_FIXOS.get(modulo)

    msg = (
        f"✅ Acesso autorizado!\n\n"
        f"🔧 *Sistema:* {dados['sistema']}\n"
        f"👤 *Usuário:* {dados['usuario']}\n"
        f"🔑 *Senha:* {dados['senha']}\n"
        f"📡 *Host:* {dados['host']}\n"
        f"📍 *Porta:* {dados['porta']}"
    )

    sent = await update.message.reply_text(msg, parse_mode="Markdown")
    await asyncio.sleep(120)
    await sent.delete()
    del usuario_modulo[user_id]

# Execução
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ao_receber_texto))

    print("✅ Bot rodando...")
    app.run_polling()

