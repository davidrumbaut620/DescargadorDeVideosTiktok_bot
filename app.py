from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from io import BytesIO
import os
import requests
from douyin_tiktok_scraper.scraper import Scraper
from dotenv import load_dotenv
import logging

logging.getLogger().setLevel(logging.CRITICAL)
load_dotenv()

api = Scraper()
token = os.getenv("7168708760:AAE5vIpLYwjeAQLuUEXIQexADCFN6JuCpQQ")
BOT_USERNAME = '@DescargadorDeVideosTiktok_bot'

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hola visita nuestra web en: https://technoh4ckstutoriales.blogspot.com/')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Por favor escriba algo para que pueda responder')

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Este es un comando personalizado')

async def hybrid_parsing(url: str) -> dict:
    try:
        # Hybrid parsing(Douyin/TikTok URL)
        result = await api.hybrid_parsing(url)

        video = result["video_data"]["nwm_video_url_HQ"]
        video_hq = result["video_data"]["nwm_video_url_HQ"]
        music = result["music"]["play_url"]["uri"]
        caption = result["desc"]

        print("Video URL:", video)
        print("Video_HQ URL:", video_hq)
        print("Play URL:", music)
        print("Caption:", caption)
        
        response_video = requests.get(video)
        response_video_hq = requests.get(video_hq)

        if response_video.status_code == 200:
            video_stream = BytesIO(response_video.content)
        else:
            print(f"No se pudo descargar MP4.Estado del Código: {response_video.status_code}")

        if response_video_hq.status_code == 200:
            video_stream_hq = BytesIO(response_video_hq.content)
        else:
            print(f"No se pudo descargar MP4.Estado del Código: {response_video_hq.status_code}")
        
    except Exception as e:
        print(f'Ocurrio un error: {str(e)}')
        return None

    return video_stream, video_stream_hq, music, caption, video_hq

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')
    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
        else:
            return
    elif message_type == 'private':
        if "tiktok.com" in text:

            result = await hybrid_parsing(text)

            if result:
                video = result[0]
                video_hq = result[1]
                music = result[2]
                caption = result[3]
                link =  result[4]
                text = "Link:\n" + link + "\n\n" + "Sound:\n" + music + "\n\n" + "Caption:\n" + caption
                text_link = "El video es demasiado grande, enviando el enlace en su lugar" + "\n\n" + "Link:\n" + link + "\n\n" + "Sound:\n" + music + "\n\n" + "Caption:\n" + caption

                try:
                    await update.message.reply_video(video=InputFile(video_hq), caption=text)
                except Exception as e:
                    if "Request Entity Too Large (413)" in str(e):
                        print("Video is too large, sending link instead")
                        await update.message.reply_text(text_link)

            else:
                await update.message.reply_text("Por favor envíe solo una URL de Tiktok")
        else:
            await update.message.reply_text("Por favor envíe una URL de Tiktok")
            return

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

if name == 'main':
    print('Starting bot...')
    app = Application.builder().token(token).build()

    
def handler(event, context):
    update = Update.de_json(event['body'], bot)
    dispatcher.process_update(update)

# Configurar comandos y manejo de mensajes...
dispatcher = Dispatcher(bot, None, workers=0)
dispatcher.add_handler(CommandHandler('start', start_command))
dispatcher.add_handler(CommandHandler('help', help_command))
dispatcher.add_handler(CommandHandler('custom', custom_command))
# Añadir más handlers si es necesario...

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))

    # Messages
     app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_handler(MessageHandler(filters.VOICE, handle_message))

    # Errors
    app.add_error_handler(error)

    # Polls the bot
    print('Polling...')
    app.run_polling(poll_interval=3)

