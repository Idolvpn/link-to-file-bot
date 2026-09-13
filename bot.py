import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# توکن ربات از محیط اجرا خوانده می‌شود
BOT_TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! لینک مستقیم فایل را بفرستید تا آن را برای شما ارسال کنم.")

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    
    if not url.startswith(('http://', 'https://')):
        await update.message.reply_text("لطفاً یک لینک معتبر ارسال کنید.")
        return

    try:
        await update.message.reply_text("در حال دانلود فایل... لطفاً صبر کنید.")
        
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        filename = url.split("/")[-1]
        if '?' in filename:
            filename = filename.split('?')[0]
        if not filename or '.' not in filename:
            filename = "downloaded_file"

        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        await update.message.reply_document(document=open(filename, 'rb'), caption=f"فایل دانلود شد: {filename}")
        
        os.remove(filename)
        
    except Exception as e:
        await update.message.reply_text(f"خطا در دانلود فایل: {str(e)}")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
