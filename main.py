import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)
import asyncio

TOKEN = os.getenv("BOT_TOKEN")
PORTA = int(os.getenv("PORT", 8080))
SENHA_CORRETA = "potiguar123"
usuario_em_espera = {}  # user_id -> módulo

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("EPORTAL", callback_data="EPORTAL")],
        [InlineKeyboardButton("PRP", callback_data="PRP")],
        [InlineKeyboardButton("AUTH", callback_data="AUTH")],
        [InlineKeyboardButton("MCS_EPORTAL", callback_data="MCS_EPORTAL")]
    ]
    await update.message.reply_text(
        "👋 Escolha um dos módulos abaixo:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# clique no botão
async def ao_clicar_modulo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    modulo = query.data
    user_id = query.from_user.id
    usuario_em_espera[user_id] = modulo
    await query.message.reply_text(f"🔒 Digite a senha para acessar o módulo *{modulo}*:", parse_mode="Markdown")

# digitação de senha
async def ao_receber_mensagem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    senha = update.message.text.strip()

    if user_id not in usuario_em_espera:
        await update.message.reply_text("❗ Envie /start para ver os módulos disponíveis.")
        return

    modulo = usuario_em_espera[user_id]

    if senha != SENHA_CORRETA:
        await update.message.reply_text("❌ Senha incorreta.")
        del usuario_em_espera[user_id]
        return

    # Mensagem conforme módulo
    if modulo == "EPORTAL":
        msg = (
            "✅ Acesso autorizado!\n\n"
            "🔧 *Sistema:* EPORTAL\n"
            "👤 *Usuário:* TESTE\n"
            "🔑 *Senha:* 123\n"
            "📡 *Host:* 192.5.5.5\n"
            "📍 *Porta:* 1515"
        )
    elif modulo == "AUTH":
        msg = (
            "✅ Acesso autorizado!\n\n"
            "🔧 *Sistema:* AUTH\n"
            "👤 *Usuário:* TESTE AUTH\n"
            "🔑 *Senha:* 12345\n"
            "📡 *Host:* 192.0.0.5\n"
            "📍 *Porta:* 1515"
        )
    elif modulo == "PRP":
        msg = (
            "✅ Acesso autorizado!\n\n"
            "🔧 *Sistema:* PRP\n"
            "👤 *Usuário:* PRP_USER\n"
            "🔑 *Senha:* 54321\n"
            "📡 *Host:* 10.10.10.10\n"
            "📍 *Porta:* 3306"
        )
    elif modulo == "MCS_EPORTAL":
        msg = (
            "✅ Acesso autorizado!\n\n"
            "🔧 *Sistema:* MCS_EPORTAL\n"
            "👤 *Usuário:* MCS_USER\n"
            "🔑 *Senha:* abc123\n"
            "📡 *Host:* 127.0.0.1\n"
            "📍 *Porta:* 8080"
        )
    else:
        msg = "❌ Módulo inválido."

    sent = await update.message.reply_text(msg, parse_mode="Markdown")
    await asyncio.sleep(120)
    await sent.delete()
    del usuario_em_espera[user_id]

# main
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(ao_clicar_modulo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ao_receber_mensagem))
    print("✅ Bot rodando com polling...")
    app.run_polling()

