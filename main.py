import os
import asyncio
import logging

# --- ⚠️ CRITICAL FIX FOR RENDER / PYTHON 3.14 ---
# Hum check nahi karenge, seedha naya loop banayenge.
# Ye line Pyrogram import hone se PEHLE honi chahiye.
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# --- AB BAKI IMPORTS KAREIN ---
import json
import re
from threading import Thread
from flask import Flask
from pyrogram import Client, filters, idle
from pyrogram.errors import PeerIdInvalid

# --- LOGGING SETUP ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- AUTHENTICATION ---
OWNER_ID = 7762163050
ADMIN_ID = 7727470646
AUTHORIZED_USERS = {OWNER_ID, ADMIN_ID}

def is_authorized(user_id):
    return user_id in AUTHORIZED_USERS

# --- WEB SERVER (Render Ke Liye) ---
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

MAIN_SOURCE_BOT = "Random_insight69_bot"
TG_LOOKUP_BOT = "Jhsgdysgshbot"

app = Client("gourisen_osint_bot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

# --- 🔐 PERMISSION COMMANDS ---
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

# --- 🆕 FEATURE: /id ---
@app.on_message(filters.command("id") & (filters.private | filters.group))
async def get_id(client, message):
    if not is_authorized(message.from_user.id): return
    if len(message.command) < 2: return await message.reply("ℹ️ Usage: `/id @username`")
    
    status = await message.reply("🔍 **Checking...**")
    try:
        user = await client.get_users(message.command[1])
        await status.edit(f"🆔 **ID:** `{user.id}`\n👤 **Name:** {user.first_name}")
    except Exception as e:
        await status.edit(f"❌ **Error:** {e}")

# --- 🆕 FEATURE: /tg ---
@app.on_message(filters.command("tg") & (filters.private | filters.group))
async def tg_lookup(client, message):
    if not is_authorized(message.from_user.id): return
    if len(message.command) < 2: return await message.reply("ℹ️ Usage: `/tg [UserID]`")

    uid = message.command[1]
    if not uid.isdigit(): return await message.reply("❌ Only Numeric IDs allowed.")

    status = await message.reply(f"🔍 **Searching ID {uid}...**")
    
    try:
        sent = await client.send_message(TG_LOOKUP_BOT, f"tg{uid}")
        target_response = None

        for _ in range(25):
            await asyncio.sleep(2)
            async for log in client.get_chat_history(TG_LOOKUP_BOT, limit=1):
                if log.id == sent.id: continue
                
                txt = (log.text or log.caption or "").lower()
                
                if "лимит" in txt or "limit" in txt:
                    await status.delete()
                    return await message.reply("⚠️ **Bro Limit Reach**")

                if "телефон" in txt or "phone" in txt:
                    target_response = log
                    break
            if target_response: break
        
        if not target_response:
            await status.edit("❌ **No Data Found**")
            return

        full_text = target_response.text or target_response.caption or ""
        match = re.search(r"(?:Телефон|Phone):\s*([0-9+]+)", full_text)

        if match:
            await status.edit(f"📞 **Phone Number:** `{match.group(1)}`")
        else:
            await status.edit("❌ **No Data Found**")

    except Exception as e:
        await status.edit(f"❌ Error: {e}")

# --- DASHBOARD ---
@app.on_message(filters.command(["start", "help", "menu"]))
async def dashboard(client, message):
    if not is_authorized(message.from_user.id): return
    text = (
        "📖 **Gourisen OSINT DASHBOARD**\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "🔍 **Lookup Services:**\n"
        "📱 `/num`  🚗 `/vehicle`  🆔 `/aadhar`\n"
        "👨‍👩‍👧‍👦 `/familyinfo`  🔗 `/vnum`  💸 `/fam`\n"
        "📨 `/sms`\n\n"
        "🆕 **New Tools:**\n"
        "👤 `/id [user]` - Get User ID\n"
        "🤖 `/tg [id]` - TG Lookup\n"
        "━━━━━━━━━━━━━━━━━━"
    )
    await message.reply(text)

# --- MAIN SEARCH ---
@app.on_message(filters.command(["num", "vehicle", "aadhar", "familyinfo", "vnum", "fam", "sms"]))
async def main_process(client, message):
    if not is_authorized(message.from_user.id): return
    if len(message.command) < 2:
        return await message.reply(f"❌ **Missing Data!**\nUsage: `/{message.command[0]} <value>`")

    status = await message.reply("🔍 **Searching via Gourisen OSINT...**")

    try:
        sent = await client.send_message(MAIN_SOURCE_BOT, message.text)
        target_response = None

        for attempt in range(30):
            await asyncio.sleep(2)
            async for log in client.get_chat_history(MAIN_SOURCE_BOT, limit=1):
                if log.id == sent.id: continue

                text_content = (log.text or log.caption or "").lower()
                ignore_words = ["wait", "processing", "searching", "scanning", "generating", "loading"]
                
                if any(w in text_content for w in ignore_words) and not log.document:
                    if attempt % 5 == 0: await status.edit(f"⏳ **Fetching... ({attempt})**")
                    continue
                
                target_response = log
                break
            if target_response: break

        if not target_response:
            await status.edit("❌ **No Data Found**")
            return

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

        raw_text = raw_text.replace(r"⚡ Designed & Powered by @DuXxZx\_info", "")
        raw_text = raw_text.replace("@DuXxZx_info", "")
        
        final_output = raw_text
        try:
            clean = raw_text.replace("```json", "").replace("```", "").strip()
            if "{" in clean:
                match = re.search(r'\{.*\}', clean, re.DOTALL)
                if match:
                    data = json.loads(match.group(0))
                    if "data" in data: data = data["data"]
                    if isinstance(data, list) and len(data) > 0 and "results" in data[0]:
                        data = data[0]["results"]
                    elif isinstance(data, dict) and "results" in data:
                        data = data["results"]
                    
                    final_output = json.dumps(data, indent=4, ensure_ascii=False)
        except: pass

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

# --- START ---
async def start_bot():
    print("🚀 Starting Web Server...")
    keep_alive()
    print("🚀 Starting Bot...")
    await app.start()
    print("✅ Gourisen OSINT Bot is Online!")
    await idle()
    await app.stop()

if __name__ == "__main__":
    # Is baar hum naye banaye hue loop ko use karenge
    loop.run_until_complete(start_bot())