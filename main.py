import os
import asyncio
import logging
import json
import re
from threading import Thread
from flask import Flask
from pyrogram import Client, filters, idle
from pyrogram.errors import PeerIdInvalid

# --- ⚠️ CRITICAL FIX FOR PYTHON 3.10+ ---
try:
    asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

# --- LOGGING SETUP ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- AUTHENTICATION CONFIG ---
OWNER_ID = 7762163050
ADMIN_ID = 7727470646
AUTHORIZED_USERS = [OWNER_ID, ADMIN_ID]

# --- FAKE WEBSITE FOR RENDER ---
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "⚡ Gourisen OSINT Bot is Running Successfully!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.daemon = True
    t.start()

# --- CONFIGURATION ---
API_ID = 37314366
API_HASH = "bd4c934697e7e91942ac911a5a287b46"
SESSION_STRING = "BQI5Xz4AYmk4kg6TAh1_7Ebt65uwpCt5ryzpfEb-DlJ-hwhK2OuYoKI9Rboc391MVc-TRBHL_eQkMYyl1WVuKq9po2r6RKIJBLPf9vzO7_fWiDSz0tC1XUDFFvX1PrmUFls8cZgJWg1TZx6EOYhlTMnXhhWfBOnHXb5orXyFlRd5sxrXCC-A-kEnmtfAi1UGuX4tgzUplpgYDQHS1lQK-vPExaML7FajZfsasoIXvOFWRndMSY3qOqhSqm-ZLIhRhaVa333weGM8z4hQqE9iuvsYFr4wwwAnYaRRSBob8MfIN5tGSyZpbT-6iOZTyx7ttqTh6mKqn0JatY3Lk1n6P7ulu3Pv_gAAAAFJSgVkAA"
TARGET_BOT = "Random_insight69_bot"

app = Client("gourisen_osint_bot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

# --- HELPER: AUTH CHECK ---
def is_authorized(user_id):
    return user_id in AUTHORIZED_USERS

# --- DASHBOARD ---
@app.on_message(filters.command(["start", "help", "menu"], prefixes="/") & (filters.private | filters.group))
async def show_dashboard(client, message):
    # Only respond if the user is authorized
    if not is_authorized(message.from_user.id):
        return 

    try:
        text = (
            "📖 **Gourisen OSINT DASHBOARD**\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "🔍 **Lookup Services:**\n"
            "📱 `/num [number]`\n🚗 `/vehicle [plate]`\n🆔 `/aadhar [uid]`\n"
            "👨‍👩‍👧‍👦 `/familyinfo [uid]`\n🔗 `/vnum [plate]`\n💸 `/fam [id]`\n📨 `/sms [number]`\n"
            "━━━━━━━━━━━━━━━━━━"
        )
        await message.reply_text(text, disable_web_page_preview=True)
    except Exception as e:
        logger.error(f"Error in dashboard: {e}")

# --- MAIN LOGIC ---
@app.on_message(filters.command(["num", "vehicle", "aadhar", "familyinfo", "vnum", "fam", "sms"], prefixes="/") & (filters.private | filters.group))
async def process_request(client, message):
    # Only respond if the user is authorized
    if not is_authorized(message.from_user.id):
        return

    try:
        if len(message.command) < 2:
            return await message.reply_text(f"❌ **Data Missing!**\nUsage: `/{message.command[0]} <value>`")

        status_msg = await message.reply_text(f"🔍 **Searching via Gourisen OSINT...**")

        try:
            sent_req = await client.send_message(TARGET_BOT, message.text)
        except PeerIdInvalid:
             await status_msg.edit("❌ **Error:** Target Bot ID invalid. Userbot must start @Random_insight69_bot first.")
             return
        except Exception as e:
            await status_msg.edit(f"❌ **Request Error:** {e}")
            return

        target_response = None

        # --- SMART WAIT LOOP ---
        for attempt in range(30): 
            await asyncio.sleep(2) 
            try:
                async for log in client.get_chat_history(TARGET_BOT, limit=1):
                    if log.id == sent_req.id: continue
                    text_content = (log.text or log.caption or "").lower()
                    ignore_words = ["wait", "processing", "searching", "scanning", "generating", "loading"]

                    if any(word in text_content for word in ignore_words) and not log.document:
                        continue 

                    target_response = log
                    break
            except Exception as e:
                logger.error(f"Error fetching history: {e}")
            if target_response: break

        if not target_response:
            await status_msg.edit("❌ **No Data Found**")
            return

        # --- DATA HANDLING ---
        raw_text = ""
        if target_response.document:
            file_path = await client.download_media(target_response)
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                raw_text = f.read()
            os.remove(file_path)
        else:
            raw_text = target_response.text or target_response.caption

        # Aggressive Cleaning (Removing original credits)
        raw_text = re.sub(r"@DuXxZx_info", "", raw_text, flags=re.IGNORECASE)

        await status_msg.delete()
        await message.reply_text(f"```json\n{raw_text[:4000]}\n```")

    except Exception as e:
        logger.error(f"Main logic error: {e}")

# --- START SERVER & BOT ---
async def start_bot():
    keep_alive() 
    await app.start()
    print("✅ Gourisen OSINT Bot is Online (Whitelist Active)!")
    await idle()
    await app.stop()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_bot())