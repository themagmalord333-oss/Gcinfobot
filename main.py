import os
import asyncio
import logging
import json
import re
from threading import Thread
from flask import Flask
from pyrogram import Client, filters, idle
from pyrogram.errors import PeerIdInvalid, UsernameInvalid

# --- ⚠️ CRITICAL FIX FOR RENDER (MUST BE AT TOP) ---
try:
    asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

# --- LOGGING ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- AUTHENTICATION (WHITELIST) ---
OWNER_ID = 7762163050
ADMIN_ID = 7727470646
AUTHORIZED_USERS = {OWNER_ID, ADMIN_ID}

def is_authorized(user_id):
    return user_id in AUTHORIZED_USERS

# --- WEB SERVER (KEEP ALIVE) ---
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "⚡ Vipbluehatnetwork OSINT Bot is Running Successfully!"

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

MAIN_SOURCE_BOT = "Backupinfo69_bot"

app = Client("vipbluehatnetwork", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

# --- 🔐 PERMISSION COMMANDS (OWNER ONLY) ---
@app.on_message(filters.command("auth") & filters.user(OWNER_ID))
async def auth_user(client, message):
    if len(message.command) < 2: return await message.reply("ℹ️ Usage: `/auth [ID]`")
    try:
        uid = int(message.command[1])
        AUTHORIZED_USERS.add(uid)
        await message.reply(f"✅ User `{uid}` Authorized!")
    except: await message.reply("❌ Invalid ID")

@app.on_message(filters.command("unauth") & filters.user(OWNER_ID))
async def unauth_user(client, message):
    if len(message.command) < 2: return await message.reply("ℹ️ Usage: `/unauth [ID]`")
    try:
        uid = int(message.command[1])
        if uid in AUTHORIZED_USERS and uid != OWNER_ID:
            AUTHORIZED_USERS.remove(uid)
            await message.reply(f"🚫 User `{uid}` Removed.")
    except: await message.reply("❌ Invalid ID")

# --- 🆕 FEATURE 1: /id (Get User ID) ---
@app.on_message(filters.command("id") & (filters.private | filters.group))
async def get_target_id(client, message):
    if not is_authorized(message.from_user.id): return
    if len(message.command) < 2: return await message.reply("ℹ️ Usage: `/id @username`")

    status = await message.reply("🔍 **Checking...**")
    try:
        user = await client.get_users(message.command[1])
        await status.edit(f"🆔 **ID:** `{user.id}`\n👤 **Name:** {user.first_name}")
    except Exception as e:
        await status.edit(f"❌ **Error:** {e}")

# --- DASHBOARD ---
@app.on_message(filters.command(["start", "help", "menu"]))
async def dashboard(client, message):
    if not is_authorized(message.from_user.id): return
    text = (
        "📖 **vipbluehatnetwork DASHBOARD**\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "🔍 **Lookup Services:**\n"
        "📱 `/num`  🚗 `/Vehicle`  🆔 `/Aadhar`\n"
        "👨‍👩‍👧‍👦 `/familyinfo`  🔗 `/Vnum`  💳 `/Pan`\n"
        "🤖 `/tgnum`\n\n"
        "🆕 **Other Tools:**\n"
        "👤 `/id [user]` - Get User ID\n"
        "━━━━━━━━━━━━━━━━━━"
    )
    await message.reply(text)

# --- MAIN SEARCH (FULL LOGIC WITH FILE DOWNLOAD) ---
@app.on_message(filters.command(["num", "Vehicle", "Aadhar", "familyinfo", "Vnum", "Pan", "tgnum"]))
async def main_process(client, message):
    if not is_authorized(message.from_user.id): return

    if len(message.command) < 2:
        return await message.reply(f"❌ **Missing Data!**\nUsage: `/{message.command[0]} <value>`")

    status = await message.reply("🔍 **Searching via vipbluehatnetwork...**")

    try:
        # Since /tgnum is just another feature now, we send the exact command to the backup bot
        sent = await client.send_message(MAIN_SOURCE_BOT, message.text)
        target_response = None

        # --- SMART WAIT LOOP ---
        for attempt in range(30):
            await asyncio.sleep(2)
            async for log in client.get_chat_history(MAIN_SOURCE_BOT, limit=1):
                if log.id == sent.id: continue

                text_content = (log.text or log.caption or "").lower()
                ignore_words = ["wait", "processing", "searching", "scanning", "generating", "loading"]

                # Agar sirf 'wait' msg hai to continue karo
                if any(w in text_content for w in ignore_words) and not log.document:
                    if attempt % 5 == 0: await status.edit(f"⏳ **Fetching... ({attempt})**")
                    continue

                target_response = log
                break
            if target_response: break

        if not target_response:
            await status.edit("❌ **No Data Found**")
            return

        # --- FILE DOWNLOAD & READING ---
        raw_text = ""
        if target_response.document:
            await status.edit("📂 **Downloading File...**")
            try:
                path = await client.download_media(target_response)
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    raw_text = f.read()
                os.remove(path)
            except Exception as e:
                return await status.edit(f"❌ File Error: {e}")
        else:
            raw_text = target_response.text or target_response.caption or ""

        if len(raw_text) < 2:
            return await status.edit("❌ **No Data Found**")

        # --- CLEANING ---
        raw_text = raw_text.replace(r"⚡ Designed & Powered by @DuXxZx\_info", "")
        raw_text = raw_text.replace("@DuXxZx_info", "")

        # --- JSON FORMATTING ---
        final_output = raw_text
        try:
            clean = raw_text.replace("```json", "").replace("```", "").strip()
            if "{" in clean:
                match = re.search(r'\{.*\}', clean, re.DOTALL)
                if match:
                    data = json.loads(match.group(0))
                    # Extract logic
                    if "data" in data: data = data["data"]
                    if isinstance(data, list) and len(data) > 0 and "results" in data[0]:
                        data = data[0]["results"]
                    elif isinstance(data, dict) and "results" in data:
                        data = data["results"]

                    final_output = json.dumps(data, indent=4, ensure_ascii=False)
        except: pass

        # --- SENDING RESULT ---
        msg = f"```json\n{final_output}\n```"
        await status.delete()

        if len(msg) > 4000:
            for x in range(0, len(msg), 4000):
                await message.reply(msg[x:x+4000])
                await asyncio.sleep(1)
        else:
            await message.reply(msg)

    except Exception as e:
        try: await status.edit(f"❌ Error: {e}")
        except: pass

# --- START SERVER & BOT ---
async def start_bot():
    print("🚀 Starting Web Server...")
    keep_alive() 
    print("🚀 Starting Bot...")
    await app.start()
    print("✅ vipbluehatnetwork Bot is Online!")
    await idle()
    await app.stop()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_bot())
