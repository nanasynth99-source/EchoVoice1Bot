import os
import sys
import time
from gtts import gTTS
import telebot

# Retrieve the bot token from Render's Environment Variables
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    print("ERROR: BOT_TOKEN environment variable is missing!", file=sys.stderr)
    sys.exit(1)

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "👋 Hello! I am your Text-to-Speech bot.\n\n"
        "Just send me any text message, and I will convert it into a voice note for you!"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
def convert_text_to_speech(message):
    # Ignore empty messages or commands
    if not message.text or message.text.startswith('/'):
        return

    # Let the user know the bot is working by showing "typing/recording" status
    bot.send_chat_action(message.chat.id, 'record_audio')
    
    file_path = f"tts_{message.message_id}.ogg"
    
    try:
        # Generate the speech using gTTS (Defaults to English 'en')
        tts = gTTS(text=message.text, lang='en', slow=False)
        tts.save(file_path)
        
        # Send the audio file back as a voice note
        with open(file_path, 'rb') as voice:
            bot.send_voice(message.chat.id, voice, reply_to_message_id=message.message_id)
            
    except Exception as e:
        print(f"Error generating speech: {e}", file=sys.stderr)
        bot.reply_to(message, "❌ Oops! Something went wrong while processing your text.")
        
    finally:
        # Clean up the file after sending or if an error occurs
        if os.path.exists(file_path):
            os.remove(file_path)

if __name__ == "__main__":
    print("Bot is starting up...")
    
    # Infinite loop to keep the background worker alive and handle connection drops
    while True:
        try:
            print("Bot is polling for messages...")
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            print(f"Polling error encountered: {e}. Reconnecting in 5 seconds...", file=sys.stderr)
            time.sleep(5)
