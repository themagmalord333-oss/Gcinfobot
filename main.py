import os
import asyncio
import logging
import json
import re
from threading import Thread
from flask import Flask
from pyrogram import Client, filters, idle

# --- ⚠️ CRITICAL FIX FOR RENDER ---
try:
    asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

# --- LOGGING ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- AUTHENTICATION ---
OWNER_ID = 7762163050
ADMIN_ID = 7727470646
AUTHORIZED_USERS = {OWNER_ID, ADMIN_ID}

def is_authorized(user_id):
    return user_id in AUTHORIZED_USERS

# --- WEB SERVER (KEEP ALIVE) ---
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "⚡ VIP BLUE HAT NETWORK Bot is Running!"

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
SESSION_STRING = "BQI5Xz4AlbuU3B5b_1PGYQuKw8hHzdc--FupA_5OTNcfpP0x_N-lTGTWVLbCbAyWVNTog5wIynXUFTi9VcsMw3FqX40tzuK7RnLT32Rcw6mdRKfZ3Dnl903ZU-4wVi_EgnE006uHqnoQjzzwlYqAr7N8dvgfDhn4-vTTj-Pvm9tTobzToT_utoHpsV1KrVVjwYNTGIqPbURAcXtrJIIN_JIcCnMoklpe3WdMAF0w-7TEOxpa9RFM-zyVafqKb1OoGGacq-B6jTNDzCtbv7Tz__dNlYkLtVwMaVE_vnOjZjECIT9Sxsc067edG9d6iXr4G0u_wcC4BR7ZpGrf1UHAp8ErefHs0wAAAAFJSgVkAA"

# Updated Target Bot
MAIN_SOURCE_BOT = "Backupinfo69_bot"

app = Client("vip_blue_hat_bot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

# --- DASHBOARD ---
@app.on_message(filters.command(["start", "help", "menu"]))
async def dashboard(client, message):
    if not is_authorized(message.from_user.id): return
    text = (
        "💙 **VIP BLUE HAT NETWORK**\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "🔍 **OSINT Services:**\n"
        "📱 `/num` - Phone Lookup\n"
        "🆔 `/aadhar` - Aadhar Details\n"
        "👨‍👩‍👧‍👦 `/familyinfo` - Family Data\n"
        "💳 `/pan` - PAN Card Details\n"
        "🚗 `/vehicle` - Vehicle Owner Info\n"
        "🔗 `/vnum` - Virtual Number Check\n"
        "🤖 `/tgnum` - Telegram ID Lookup\n"
        "━━━━━━━━━━━━━━━━━━"
    )
    await message.reply(text)

# --- MAIN OSINT PROCESSOR ---
@app.on_message(filters.command(["num", "aadhar", "familyinfo", "pan", "vehicle", "vnum", "tgnum"]))
async def main_process(client, message):
    if not is_authorized(message.from_user.id): return

    if len(message.command) < 2:
        return await message.reply(f"❌ Usage: `/{message.command[0]} <value>`")

    cmd = message.command[0].lower()
    query = message.text

    # Custom handling for tgnum to match source bot format if needed
    if cmd == "tgnum":
        # If the source bot requires "tg" prefix for IDs
        query = f"/tg {message.command[1]}"

    status = await message.reply("🛰 **Processing Request...**")

    try:
        sent = await client.send_message(MAIN_SOURCE_BOT, query)
        target_response = None

        for attempt in range(30):
            await asyncio.sleep(2)
            async for log in client.get_chat_history(MAIN_SOURCE_BOT, limit=1):
                if log.id <= sent.id: continue
                
                text_content = (log.text or log.caption or "").lower()
                ignore_words = ["wait", "processing", "searching", "scanning"]

                if any(w in text_content for w in ignore_words) and not log.document:
                    continue

                target_response = log
                break
            if target_response: break

        if not target_response:
            return await status.edit("❌ **No response from source bot.**")

        # Handling Result (Text or File)
        final_output = ""
        if target_response.document:
            path = await client.download_media(target_response)
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                final_output = f.read()
            os.remove(path)
        else:
            final_output = target_response.text or target_response.caption or ""

        # Check for Limits
        if "limit" in final_output.lower() or "лимит" in final_output.lower():
            return await status.edit("⚠️ **API Limit Reached on Source Bot.**")

        # Clean branding
        final_output = re.sub(r"@[A-Za-z0-9_]+", "", final_output).strip()

        await status.delete()
        
        # Send in chunks if too long
        if len(final_output) > 4000:
            for x in range(0, len(final_output), 4000):
                await message.reply(f"```json\n{final_output[x:x+4000]}\n```")
        else:
            await message.reply(f"```json\n{final_output}\n```")

    except Exception as e:
        await status.edit(f"❌ **Error:** {str(e)}")

# --- STARTUP ---
async def start_bot():
    keep_alive() 
    await app.start()
    print("✅ VIP BLUE HAT NETWORK is Online!")
    await idle()
    await app.stop()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(start_bot())
