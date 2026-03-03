import os
import asyncio
import logging
import json
import re
from threading import Thread
from flask import Flask
from pyrogram import Client, filters, idle

# --- RENDER STABILITY FIX ---
try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

# --- LOGGING ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- CONFIG ---
API_ID = 37314366
API_HASH = "bd4c934697e7e91942ac911a5a287b46"
SESSION_STRING = "BQI5Xz4AlbuU3B5b_1PGYQuKw8hHzdc--FupA_5OTNcfpP0x_N-lTGTWVLbCbAyWVNTog5wIynXUFTi9VcsMw3FqX40tzuK7RnLT32Rcw6mdRKfZ3Dnl903ZU-4wVi_EgnE006uHqnoQjzzwlYqAr7N8dvgfDhn4-vTTj-Pvm9tTobzToT_utoHpsV1KrVVjwYNTGIqPbURAcXtrJIIN_JIcCnMoklpe3WdMAF0w-7TEOxpa9RFM-zyVafqKb1OoGGacq-B6jTNDzCtbv7Tz__dNlYkLtVwMaVE_vnOjZjECIT9Sxsc067edG9d6iXr4G0u_wcC4BR7ZpGrf1UHAp8ErefHs0wAAAAFJSgVkAA"

MAIN_SOURCE_BOT = "Backupinfo69_bot"
OWNER_ID = 7762163050
ADMIN_ID = 7727470646
AUTHORIZED_USERS = {OWNER_ID, ADMIN_ID}

app = Client("vip_blue_hat_bot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

# --- WEB SERVER (KEEP ALIVE) ---
web_app = Flask(__name__)
@web_app.route('/')
def home(): return "⚡ VIP BLUE HAT NETWORK is Online!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)

# --- AUTH LOGIC ---
def is_authorized(uid): return uid in AUTHORIZED_USERS

@app.on_message(filters.command("auth") & filters.user(OWNER_ID))
async def auth_user(c, m):
    if len(m.command) < 2: return await m.reply("ℹ️ Usage: `/auth [ID]`")
    AUTHORIZED_USERS.add(int(m.command[1]))
    await m.reply(f"✅ User `{m.command[1]}` Authorized!")

@app.on_message(filters.command("unauth") & filters.user(OWNER_ID))
async def unauth_user(c, m):
    if len(m.command) < 2: return await m.reply("ℹ️ Usage: `/unauth [ID]`")
    uid = int(m.command[1])
    if uid in AUTHORIZED_USERS and uid != OWNER_ID:
        AUTHORIZED_USERS.remove(uid)
        await m.reply(f"🚫 User `{uid}` Removed.")

# --- DASHBOARD ---
@app.on_message(filters.command(["start", "help", "menu"]))
async def dashboard(c, m):
    if not is_authorized(m.from_user.id): return
    await m.reply(
        "📖 **VIP BLUE HAT NETWORK**\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "📱 `/num` | 🆔 `/aadhar` | 👨‍👩‍👧‍👦 `/familyinfo` \n"
        "💳 `/pan` | 🚗 `/vehicle` | 🔗 `/vnum` \n"
        "🤖 `/tgnum` (Telegram Lookup)\n"
        "━━━━━━━━━━━━━━━━━━"
    )

# --- MAIN PROCESSOR ---
@app.on_message(filters.command(["num", "aadhar", "familyinfo", "pan", "vehicle", "vnum", "tgnum"]))
async def main_process(c, m):
    if not is_authorized(m.from_user.id): return
    if len(m.command) < 2: return await m.reply(f"❌ Usage: `/{m.command[0]} <value>`")

    status = await m.reply("🛰 **Processing...**")
    
    # Logic adjustment for tgnum
    cmd = m.command[0].lower()
    val = m.command[1]
    query = f"/tg {val}" if cmd == "tgnum" else f"/{cmd} {val}"

    try:
        sent = await c.send_message(MAIN_SOURCE_BOT, query)
        
        for _ in range(20): # 40 seconds max wait
            await asyncio.sleep(2)
            async for resp in c.get_chat_history(MAIN_SOURCE_BOT, limit=1):
                if resp.id <= sent.id: continue
                
                txt = (resp.text or resp.caption or "").lower()
                if any(x in txt for x in ["wait", "searching", "fetching"]): continue

                # Result Delivery
                if resp.document:
                    file_path = await c.download_media(resp)
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        data = f.read()
                    os.remove(file_path)
                    await status.delete()
                    return await m.reply(f"```json\n{data[:3900]}\n```")
                else:
                    await status.delete()
                    return await m.reply(f"```json\n{(resp.text or resp.caption)[:3900]}\n```")
        
        await status.edit("❌ Source Bot Time Out.")
    except Exception as e:
        await status.edit(f"❌ Error: {e}")

# --- STARTUP ---
async def start_bot():
    Thread(target=run_web, daemon=True).start()
    await app.start()
    print("✅ BOT IS ONLINE")
    await idle()

if __name__ == "__main__":
    loop.run_until_complete(start_bot())
