import os 
from gtts import gTTS
from pyrogram import Client, filters
from pyrogram.enums import ChatAction, ParseMode
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
from config import API_ID, API_HASH, BOT_TOKEN

app = Client("message_handler_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start_command(bot, message):
    try:
        await message.reply_video(
            video="https://files.catbox.moe/qdtfhq.mp4",
            caption=(
                "🌟 Welcome to Healix AI – Your Virtual Health Companion! 🌟\n\n👨‍⚕️ What Can I Do?\n"
                "🔹 Analyze your symptoms\n"
                "🔹 Predict potential diseases\n🔹 Provide remedies, precautions, and wellness tips\n\n🔹 Provide remedies, precautions, and wellness tips\n\n"
                "✨ How Does It Work?\n✅ Simple & Quick! Just type in your symptoms, and I'll provide accurate, AI-powered health insights instantly!\n\n"
                "Let’s make your health journey smarter, faster, and easier! 💖\n\n🌐 Stay Connected with Us!\n[🌍 Website](https://healixai.tech) | [💬 Telegram](https://t.me/HealixAi) | [🐦 Twitter](https://x.com/Healix__AI)."
            ),
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        print(f"Error in /start command: {e}")
        await message.reply_text("❍ ᴇʀʀᴏʀ: Unable to process the command.")

# Handler for the /doctor command
@app.on_message(filters.command("doctor") & filters.group)
async def fetch_med_info(client, message):
    query = " ".join(message.command[1:])  # Extract the query after the command
    if not query:
        await message.reply_text("Please provide a medical query to ask.")
        return

    # Send typing action to indicate bot is working
    await client.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

    # Use the API to get medical data
    api_url = f"https://medical.codesearch.workers.dev/?chat={query}"
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            reply = data.get("data", "Sorry, I couldn't fetch the data.")
        else:
            reply = "Failed to fetch data from the API."
    except Exception as e:
        reply = f"An error occurred: {e}"

    # Reply to the user
    await message.reply_text(reply)

# Handler for private message queries (DM/PM), ignoring commands
from pyrogram import filters, Client
from pyrogram.types import ChatAction
import requests

# Define the API URL
third_api_url = "https://api-ru0x.onrender.com/v1/chat/api"

# Define the payload function
def third_api_payload(user_input: str):
    return {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "system",
                "content": "Zenith AI: Your Fitness Companion. Ask me anything about exercise, nutrition, workout tips, or mental well-being. I'm here to help you achieve your health and fitness goals.",
            },
            {"role": "assistant", "content": "Instructions applied and understood."},
            {"role": "user", "content": user_input},
        ],
    }

# Define headers
headers = {
    "Content-Type": "application/json"
}

# Function to interact with the API
def interact_with_api(user_input):
    try:
        payload = third_api_payload(user_input)
        response = requests.post(third_api_url, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json().get("messages", [{}])[-1].get("content", "No response received.")
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"An error occurred: {e}"

# Bot handler for private queries
@app.on_message(filters.private & ~filters.command(["start", "doctor"]))
async def handle_private_query(client, message):
    query = message.text.strip()  # Use the message text as the query
    if not query:
        await message.reply_text("Please provide a fitness query.")  # Inform the user if no query is provided
        return

    # Send typing action to indicate the bot is working
    await client.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

    # Interact with the API
    reply = interact_with_api(query)

    # Reply to the user
    await message.reply_text(reply)


@app.on_message(filters.command("tts"))
async def text_to_speech(client, message):
    # Extract text from the command or the replied message
    text = None

    if len(message.command) > 1:
        # If the command has additional text, use it
        text = message.text.split(' ', 1)[1]
    elif message.reply_to_message and message.reply_to_message.text:
        # If replying to a message with text, use that text
        text = message.reply_to_message.text

    if not text:
        await message.reply_text("Usage: `/tts4 <text>` or reply to a text message with `/tts4`.")
        return

    try:
        # Generate TTS audio
        tts = gTTS(text=text, lang='pa')
        audio_file = 'MedicalAi_audio.mp3'
        tts.save(audio_file)
        
        # Send the audio file
        await message.reply_audio(audio_file)
    except Exception as e:
        # Handle errors
        await message.reply_text(f"An error occurred: {str(e)}")
    finally:
        # Clean up the saved audio file
        if os.path.exists(audio_file):
            os.remove(audio_file)

if __name__ == "__main__":
    print("Bot is running...")
    app.run()
