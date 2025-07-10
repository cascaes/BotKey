import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("❌ BOT_TOKEN não definido nas variáveis de ambiente!")

ARQUIVO = "mensagem.txt"
SENHA_ESPERADA = "potiguar123"

# Armazena estado do usuário (usuário_id -> módulo_escolhido)
estado_usuarios = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Olá! Use o comando /acesso para visualizar os módulos disponíveis.")

async def acesso(update: Update, context: ContextTypes.DEFAULT_TYPE):
    teclado = [
        [InlineKeyboardButton("EPORTAL", callback_data="mod:EPORTAL")],
        [InlineKeyboardButton("PRP", callback_data="mod:PRP")],
        [InlineKeyboardButton("AUTH", callback_data="mod:AUTH")],
        [InlineKeyboardButton("MCS_EPORTAL", callback_data="mod:MCS_EPORTAL")],
    ]
    await update.message.reply_text(
        "Escolha o módulo:",
        reply_markup=InlineKeyboardMarkup(teclado)
    )

async def botao_clicado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("mod:"):
        modulo = query.data.split(":")[1]
        estado_usuarios[query.from_user.id] = modulo
        await query.message.reply_text(f"🔐 Digite a senha para acessar o módulo *{modulo}*:", parse_mode="Markdown")

async def processar_senha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    senha = update.message.text.strip()

    if user_id not in estado_usuarios:
        await update.message.reply_text("❌ Nenhum módulo foi selecionado. Use o comando /acesso.")
        return

    if senha != SENHA_ESPERADA:
        await update.message.reply_text("❌ Senha incorreta.")
        return

    modulo = estado_usuarios.pop(user_id)
    credenciais = await buscar_credenciais(modulo)

    if credenciais is None:
        await update.message.reply_text("❌ Módulo não encontrado.")
        return

    msg = (
        f"✅ Acesso autorizado!\n\n"
        f"🔧 *Sistema:* {credenciais['sistema']}\n"
        f"👤 *Usuário:* {credenciais['usuario']}\n"
        f"🔑 *Senha:* {credenciais['senha']}\n"
        f"📡 *Host:* {credenciais['host']}\n"
        f"📍 *Porta:* {credenciais['porta']}"
    )

    sent = await update.message.reply_text(msg, parse_mode="Markdown")
    await asyncio.sleep(120)
    await sent.delete()

async def buscar_credenciais(modulo: str):
    try:
        with open(ARQUIVO, "r", encoding="utf-8") as f:
            linhas = [l.strip() for l in f if l.strip()]
    except:
        return None

    for linha in linhas:
        partes = linha.split(";")
        if partes[0].strip().upper() == modulo.upper():
            return {
                "sistema": partes[0].strip() if len(partes) > 0 else "-",
                "usuario": partes[1].strip() if len(partes) > 1 else "-",
                "senha": partes[2].strip() if len(partes) > 2 else "-",
                "host": partes[3].strip() if len(partes) > 3 else "-",
                "porta": partes[4].strip() if len(partes) > 4 else "-",
            }
    return None

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("acesso", acesso))
    app.add_handler(CallbackQueryHandler(botao_clicado))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, processar_senha))

    print("Bot rodando...")
    app.run_polling()

