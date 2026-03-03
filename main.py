import os
import asyncio
import logging
import json
import re
from threading import Thread
from flask import Flask
from pyrogram import Client, filters, idle

# --- ⚠️ RENDER CRITICAL FIX (DO NOT REMOVE) ---
try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

# --- LOGGING ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- CONFIGURATION ---
API_ID = 37314366
API_HASH = "bd4c934697e7e91942ac911a5a287b46"
SESSION_STRING = "BQI5Xz4AlbuU3B5b_1PGYQuKw8hHzdc--FupA_5OTNcfpP0x_N-lTGTWVLbCbAyWVNTog5wIynXUFTi9VcsMw3FqX40tzuK7RnLT32Rcw6mdRKfZ3Dnl903ZU-4wVi_EgnE006uHqnoQjzzwlYqAr7N8dvgfDhn4-vTTj-Pvm9tTobzToT_utoHpsV1KrVVjwYNTGIqPbURAcXtrJIIN_JIcCnMoklpe3WdMAF0w-7TEOxpa9RFM-zyVafqKb1OoGGacq-B6jTNDzCtbv7Tz__dNlYkLtVwMaVE_vnOjZjECIT9Sxsc067edG9d6iXr4G0u_wcC4BR7ZpGrf1UHAp8ErefHs0wAAAAFJSgVkAA"

MAIN_SOURCE_BOT = "Backupinfo69_bot" # Naya Target Bot
OWNER_ID = 7762163050
ADMIN_ID = 7727470646
AUTHORIZED_USERS = {OWNER_ID, ADMIN_ID}

app = Client("vip_blue_hat", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

# --- WEB SERVER (KEEP ALIVE) ---
web_app = Flask(__name__)
@web_app.route('/')
def home(): return "⚡ VIP BLUE HAT NETWORK is Running!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)

# --- PERMISSIONS ---
def is_authorized(user_id):
    return user_id in AUTHORIZED_USERS

@app.on_message(filters.command("auth") & filters.user(OWNER_ID))
async def auth_user(client, message):
    try:
        uid = int(message.command[1])
        AUTHORIZED_USERS.add(uid)
        await message.reply(f"✅ User `{uid}` Authorized!")
    except: await message.reply("ℹ️ Usage: `/auth [ID]`")

@app.on_message(filters.command("unauth") & filters.user(OWNER_ID))
async def unauth_user(client, message):
    try:
        uid = int(message.command[1])
        if uid in AUTHORIZED_USERS and uid != OWNER_ID:
            AUTHORIZED_USERS.remove(uid)
            await message.reply(f"🚫 User `{uid}` Removed.")
    except: await message.reply("ℹ️ Usage: `/unauth [ID]`")

# --- DASHBOARD ---
@app.on_message(filters.command(["start", "help", "menu"]))
async def dashboard(client, message):
    if not is_authorized(message.from_user.id): return
    text = (
        "📖 **VIP BLUE HAT NETWORK**\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "🔍 **OSINT Services:**\n"
        "📱 `/num` | 🆔 `/aadhar` | 👨‍👩‍👧‍👦 `/familyinfo` \n"
        "💳 `/pan` | 🚗 `/vehicle` | 🔗 `/vnum` \n"
        "🤖 `/tgnum` (Telegram Lookup)\n"
        "━━━━━━━━━━━━━━━━━━"
    )
    await message.reply(text)

# --- MAIN LOGIC ---
@app.on_message(filters.command(["num", "aadhar", "familyinfo", "pan", "vehicle", "vnum", "tgnum"]))
async def main_process(client, message):
    if not is_authorized(message.from_user.id): return
    if len(message.command) < 2:
        return await message.reply(f"❌ Usage: `/{message.command[0]} <value>`")

    status = await message.reply("🛰 **Gourisen OSINT Fetching...**")
    
    # Tgnum ko /tg mein convert karne ke liye
    cmd = message.command[0].lower()
    value = message.command[1]
    final_query = f"/tg {value}" if cmd == "tgnum" else f"/{cmd} {value}"

    try:
        sent = await client.send_message(MAIN_SOURCE_BOT, final_query)
        
        # Smart Wait Loop
        for attempt in range(20):
            await asyncio.sleep(2)
            async for log in client.get_chat_history(MAIN_SOURCE_BOT, limit=1):
                if log.id <= sent.id: continue
                
                txt = (log.text or log.caption or "").lower()
                if any(w in txt for w in ["wait", "processing", "searching"]): continue

                # Data Response Handling
                if log.document:
                    path = await client.download_media(log)
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        raw_data = f.read()
                    os.remove(path)
                    await status.delete()
                    return await message.reply(f"```json\n{raw_data[:3900]}\n```")
                else:
                    await status.delete()
                    return await message.reply(f"```json\n{(log.text or log.caption)[:3900]}\n```")
        
        await status.edit("❌ **No Data Found (Timeout)**")
    except Exception as e:
        await status.edit(f"❌ Error: {e}")

# --- START ---
async def start_bot():
    Thread(target=run_web, daemon=True).start()
    await app.start()
    print("✅ VIP BLUE HAT BOT ONLINE")
    await idle()

if __name__ == "__main__":
    loop.run_until_complete(start_bot())
