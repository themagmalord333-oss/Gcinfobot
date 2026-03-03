import os
import asyncio
import logging
import json
import re
from threading import Thread
from flask import Flask
from pyrogram import Client, filters, idle

# --- RENDER PORT BINDING ---
web_app = Flask(__name__)
@web_app.route('/')
def home(): return "VIP BLUE HAT IS RUNNING ⚡"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)

# --- BOT CONFIG ---
API_ID = 37314366
API_HASH = "bd4c934697e7e91942ac911a5a287b46"
SESSION_STRING = "BQI5Xz4AlbuU3B5b_1PGYQuKw8hHzdc--FupA_5OTNcfpP0x_N-lTGTWVLbCbAyWVNTog5wIynXUFTi9VcsMw3FqX40tzuK7RnLT32Rcw6mdRKfZ3Dnl903ZU-4wVi_EgnE006uHqnoQjzzwlYqAr7N8dvgfDhn4-vTTj-Pvm9tTobzToT_utoHpsV1KrVVjwYNTGIqPbURAcXtrJIIN_JIcCnMoklpe3WdMAF0w-7TEOxpa9RFM-zyVafqKb1OoGGacq-B6jTNDzCtbv7Tz__dNlYkLtVwMaVE_vnOjZjECIT9Sxsc067edG9d6iXr4G0u_wcC4BR7ZpGrf1UHAp8ErefHs0wAAAAFJSgVkAA"

MAIN_SOURCE_BOT = "Backupinfo69_bot"
OWNER_ID = 7762163050
ADMIN_ID = 7727470646
AUTHORIZED_USERS = {OWNER_ID, ADMIN_ID}

app = Client("vip_blue_hat", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

# --- UTILS ---
def is_auth(uid): return uid in AUTHORIZED_USERS

# --- COMMANDS ---
@app.on_message(filters.command(["start", "help"]))
async def start(c, m):
    if not is_auth(m.from_user.id): return
    await m.reply("💙 **VIP BLUE HAT NETWORK**\n━━━━━━━━━━━━━━\nCommands: `/num`, `/Aadhar`, `/Familyinfo`, `/Pan`, `/Vehicle`, `/Vnum`, `/tgnum`")

@app.on_message(filters.command(["num", "Aadhar", "Familyinfo", "Pan", "Vehicle", "Vnum", "tgnum"]))
async def osint_handler(c, m):
    if not is_auth(m.from_user.id): return
    if len(m.command) < 2: return await m.reply(f"ℹ️ Usage: `/{m.command[0]} <value>`")

    # Mapping /tgnum to /tg for the source bot
    cmd = m.command[0].lower()
    val = m.command[1]
    query = f"/tg {val}" if cmd == "tgnum" else f"/{cmd} {val}"

    status = await m.reply("🔎 **Searching...**")
    
    try:
        sent = await c.send_message(MAIN_SOURCE_BOT, query)
        
        # Wait for 30 seconds max
        for _ in range(15):
            await asyncio.sleep(2)
            async for msg in c.get_chat_history(MAIN_SOURCE_BOT, limit=3):
                if msg.id <= sent.id: continue
                
                text = (msg.text or msg.caption or "").lower()
                if any(w in text for w in ["wait", "process", "search"]): continue

                # Got result
                if msg.document:
                    file = await c.download_media(msg)
                    with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                        data = f.read()
                    os.remove(file)
                    await status.edit(f"```json\n{data[:3900]}\n```")
                else:
                    await status.edit(f"```json\n{(msg.text or msg.caption)[:3900]}\n```")
                return
        await status.edit("❌ No Response from Source.")
    except Exception as e:
        await status.edit(f"❌ Error: {e}")

# --- RUN ---
if __name__ == "__main__":
    Thread(target=run_web, daemon=True).start()
    app.run()
