import os
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes
)

# Configurações
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("❌ BOT_TOKEN não definido!")

ARQUIVO = "mensagem.txt"
SENHA_CORRETA = "potiguar123"
PORTA = int(os.getenv("PORT", 8080))

# Estado temporário
usuario_em_espera = {}  # user_id -> módulo escolhido


# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensagem = (
        "Escolha um dos módulos abaixo clicando no menu ou enviando como comando:\n\n"
        "👉 `/eportal`\n"
        "👉 `/prp`\n"
        "👉 `/auth`\n"
        "👉 `/mcs_eportal`\n\n"
        "_Depois de escolher, digite a senha para acessar._"
    )
    await update.message.reply_text(mensagem, parse_mode="Markdown")


# Função chamada pelos comandos de módulo
async def selecionar_modulo(update: Update, context: ContextTypes.DEFAULT_TYPE, modulo: str):
    user_id = update.effective_user.id
    usuario_em_espera[user_id] = modulo
    await update.message.reply_text(f"🔒 Digite a senha para acessar o módulo *{modulo}*:", parse_mode="Markdown")


# Ao receber mensagem (verifica senha)
async def ao_receber_mensagem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    senha = update.message.text.strip()

    if user_id not in usuario_em_espera:
        await update.message.reply_text("❗ Escolha um módulo primeiro usando o menu ou /start.")
        return

    modulo = usuario_em_espera[user_id]

    if senha != SENHA_CORRETA:
        await update.message.reply_text("❌ Senha incorreta.")
        del usuario_em_espera[user_id]
        return

    try:
        with open(ARQUIVO, "r", encoding="utf-8") as f:
            linhas = [l.strip() for l in f if l.startswith("/acesso") and modulo.upper() in l]
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


# Início do bot com polling
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    # Comando inicial
    app.add_handler(CommandHandler("start", start))

    # Comandos de módulo
    app.add_handler(CommandHandler("eportal", lambda u, c: selecionar_modulo(u, c, "EPORTAL")))
    app.add_handler(CommandHandler("prp", lambda u, c: selecionar_modulo(u, c, "PRP")))
    app.add_handler(CommandHandler("auth", lambda u, c: selecionar_modulo(u, c, "AUTH")))
    app.add_handler(CommandHandler("mcs_eportal", lambda u, c: selecionar_modulo(u, c, "MCS_EPORTAL")))

    # Recebe senha
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ao_receber_mensagem))

    print("✅ Bot rodando com polling...")
    app.run_polling()

