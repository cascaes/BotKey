import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes
)
import asyncio

# Token e configurações
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("❌ BOT_TOKEN não definido!")

ARQUIVO = "mensagem.txt"
SENHA_CORRETA = "potiguar123"
PORTA = int(os.getenv("PORT", 8080))

usuario_em_espera = {}  # user_id -> módulo escolhido

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensagem = (
        "Escolha um dos módulos abaixo e envie como mensagem:\n\n"
        "👉 *EPORTAL*\n"
        "👉 *PRP*\n"
        "👉 *AUTH*\n"
        "👉 *MCS_EPORTAL*\n\n"
        "_Digite exatamente como está acima para continuar._"
    )
    await update.message.reply_text(mensagem, parse_mode="Markdown")

# Ao receber qualquer texto
async def ao_receber_mensagem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    texto = update.message.text.strip().upper()

    # Usuário escolheu um módulo
    if texto in {"EPORTAL", "PRP", "AUTH", "MCS_EPORTAL"}:
        usuario_em_espera[user_id] = texto
        await update.message.reply_text(f"🔒 Digite a senha para acessar o módulo *{texto}*:", parse_mode="Markdown")
        return

    # Nenhum módulo selecionado ainda
    if user_id not in usuario_em_espera:
        await update.message.reply_text("❗ Envie /start para ver os módulos disponíveis.")
        return

    senha = texto
    modulo = usuario_em_espera[user_id]

    # Senha errada
    if senha != SENHA_CORRETA:
        await update.message.reply_text("❌ Senha incorreta.")
        del usuario_em_espera[user_id]
        return

    # Leitura do arquivo com as credenciais
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

# --- Execução com polling (evita problemas com webhook) ---
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ao_receber_mensagem))

    print("Bot rodando com polling...")
    app.run_polling()

