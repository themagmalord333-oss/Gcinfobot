import os
import asyncio
import logging
import json
import re
from threading import Thread
from flask import Flask
from pyrogram import Client, filters, idle

# --- RENDER CRITICAL FIX ---
try:
    asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

# --- LOGGING ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- AUTH SYSTEM ---
OWNER_ID = 7762163050
ADMIN_ID = 7727470646
AUTHORIZED_USERS = {OWNER_ID, ADMIN_ID}

def is_authorized(user_id):
    return user_id in AUTHORIZED_USERS

# --- WEB SERVER ---
web_app = Flask(__name__)
@web_app.route('/')
def home(): return "⚡ VIP BLUE HAT NETWORK is Online!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)

# --- CONFIG ---
API_ID = 37314366
API_HASH = "bd4c934697e7e91942ac911a5a287b46"
SESSION_STRING = "BQI5Xz4AlbuU3B5b_1PGYQuKw8hHzdc--FupA_5OTNcfpP0x_N-lTGTWVLbCbAyWVNTog5wIynXUFTi9VcsMw3FqX40tzuK7RnLT32Rcw6mdRKfZ3Dnl903ZU-4wVi_EgnE006uHqnoQjzzwlYqAr7N8dvgfDhn4-vTTj-Pvm9tTobzToT_utoHpsV1KrVVjwYNTGIqPbURAcXtrJIIN_JIcCnMoklpe3WdMAF0w-7TEOxpa9RFM-zyVafqKb1OoGGacq-B6jTNDzCtbv7Tz__dNlYkLtVwMaVE_vnOjZjECIT9Sxsc067edG9d6iXr4G0u_wcC4BR7ZpGrf1UHAp8ErefHs0wAAAAFJSgVkAA"

MAIN_SOURCE_BOT = "Backupinfo69_bot"

app = Client("vip_blue_hat", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

# --- COMMANDS: AUTH ---
@app.on_message(filters.command("auth") & filters.user(OWNER_ID))
async def auth_user(client, message):
    if len(message.command) < 2: return await message.reply("ℹ️ `/auth [ID]`")
    uid = int(message.command[1])
    AUTHORIZED_USERS.add(uid)
    await message.reply(f"✅ `{uid}` Authorized!")

@app.on_message(filters.command("unauth") & filters.user(OWNER_ID))
async def unauth_user(client, message):
    if len(message.command) < 2: return await message.reply("ℹ️ `/unauth [ID]`")
    uid = int(message.command[1])
    if uid in AUTHORIZED_USERS and uid != OWNER_ID:
        AUTHORIZED_USERS.remove(uid)
        await message.reply(f"🚫 `{uid}` Removed.")

# --- DASHBOARD ---
@app.on_message(filters.command(["start", "help", "menu"]))
async def dashboard(client, message):
    if not is_authorized(message.from_user.id): return
    text = (
        "💙 **VIP BLUE HAT NETWORK**\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "📱 `/num` | 🆔 `/aadhar` | 💳 `/pan`\n"
        "🚗 `/vehicle` | 👨‍👩‍👧‍👦 `/familyinfo` | 🔗 `/vnum`\n"
        "🤖 `/tgnum` (Telegram Lookup)\n"
        "━━━━━━━━━━━━━━━━━━"
    )
    await message.reply(text)

# --- MASTER PROCESSOR (FOR ALL FEATURES) ---
@app.on_message(filters.command(["num", "aadhar", "pan", "vehicle", "familyinfo", "vnum", "tgnum"]))
async def main_process(client, message):
    if not is_authorized(message.from_user.id): return
    if len(message.command) < 2:
        return await message.reply(f"❌ Usage: `/{message.command[0]} <value>`")

    status = await message.reply("🛰 **Fetching Data...**")
    
    # Logic for /tgnum to send /tg to the source bot
    cmd = message.command[0].lower()
    val = message.command[1]
    send_text = f"/{cmd} {val}" if cmd != "tgnum" else f"/tg {val}"

    try:
        sent = await client.send_message(MAIN_SOURCE_BOT, send_text)
        
        for _ in range(15): # 30 seconds wait
            await asyncio.sleep(2)
            async for log in client.get_chat_history(MAIN_SOURCE_BOT, limit=1):
                if log.id <= sent.id: continue
                
                # Check for response
                res_text = (log.text or log.caption or "").lower()
                if any(x in res_text for x in ["wait", "searching", "loading"]): continue

                # Send Result
                if log.document:
                    path = await client.download_media(log)
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        final_data = f.read()
                    os.remove(path)
                    await status.edit(f"```json\n{final_data[:3900]}\n```")
                else:
                    await status.edit(f"```json\n{(log.text or log.caption)[:3900]}\n```")
                return
        await status.edit("❌ Source Bot Time Out.")
    except Exception as e:
        await status.edit(f"❌ Error: {e}")

# --- STARTUP ---
async def start_all():
    Thread(target=run_web, daemon=True).start()
    await app.start()
    print("✅ VIP BLUE HAT ONLINE")
    await idle()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(start_all())
