import os
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# --- 🛑 SABSE PEHLE EVENT LOOP BANAO (CRITICAL FIX) 🛑 ---
import asyncio
try:
    loop = asyncio.get_running_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

# --- AB BAAKI SAB IMPORT KARO ---
import logging
import json
import re
from threading import Thread
from flask import Flask
from pyrogram import Client, filters, idle

# --- LOGGING SETUP ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- WEB SERVER (FOR RENDER/UPTIME) ---
web_app = Flask(__name__)
@web_app.route('/')
def home():
    bot_name = os.getenv("BOT_NAME", "VIP BLUE HAT NETWORK")
    return f"🤖 {bot_name.upper()} is Running!"

def run_web():
    port = int(os.getenv("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)

# --- CONFIGURATION FROM ENV ---
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")

TARGET_BOT = os.getenv("TARGET_BOT")
BOT_NAME = os.getenv("BOT_NAME")

OWNER_ID = int(os.getenv("OWNER_ID"))
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# List to store authorized user IDs
AUTHORIZED_USERS = [OWNER_ID, ADMIN_ID]

app = Client("vip_blue_hat", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

# --- TEST COMMAND (BOT CHECK KARNE KE LIYE) ---
@app.on_message(filters.command("ping", prefixes=["/", ".", "!"]) & filters.private)
async def ping_cmd(client, message):
    await message.reply_text("🏓 **Pong! Bot zinda hai aur response de raha hai!**")

# --- COMMAND: AUTHENTICATE USER ---
@app.on_message(filters.command("auth", prefixes=["/", ".", "!"]) & filters.private)
async def authorize_user(client, message):
    if message.from_user.id not in [OWNER_ID, ADMIN_ID]:
        return await message.reply_text("🚫 **Aap Owner ya Admin nahi hain!**")

    if len(message.command) < 2:
        return await message.reply_text("❌ **Format Galat Hai!**\nUse: `/auth [User_ID]`")

    try:
        user_id = int(message.command[1])
        if user_id not in AUTHORIZED_USERS:
            AUTHORIZED_USERS.append(user_id)
            await message.reply_text(f"✅ User `{user_id}` ko successfully permission mil gayi hai.")
        else:
            await message.reply_text("ℹ️ Ye User pehle se authorized hai.")
    except ValueError:
        await message.reply_text("❌ **Invalid User ID!** Sirf numbers daalein.")

# --- DASHBOARD / START ---
@app.on_message(filters.command(["start", "help", "menu"], prefixes=["/", ".", "!"]) & filters.private)
async def start_cmd(client, message):
    if message.from_user.id not in AUTHORIZED_USERS:
        return await message.reply_text("🚫 **Access Denied.**\nIse use karne ke liye Admin ya Owner se permission lein.")

    text = (
        f"🛡️ **Welcome to {BOT_NAME.upper()}**\n\n"
        "**Available Commands:**\n"
        "📱 `/num [number]` → Number Details\n"
        "🚗 `/vehicle [Plate]` → Challan And Rc\n"
        "🆔 `/aadhar [UID]` → Aadhaar Info\n"
        "👨‍👩‍👧 `/familyinfo [aadhar]` → Family Tree\n"
        "🔗 `/vnum [Plate]` → Linked Mobile\n"
        "📞 `/tgnum [TG ID]` → User's Mobile\n\n"
        f"⚡ **Powered by {BOT_NAME.upper()}**"
    )
    await message.reply_text(text)

# --- MAIN LOOKUP LOGIC ---
@app.on_message(filters.command(["num", "vehicle", "aadhar", "familyinfo", "vnum", "tgnum", "fam", "sms"], prefixes=["/", ".", "!"]) & filters.private)
async def process_lookup(client, message):
    if message.from_user.id not in AUTHORIZED_USERS:
        return await message.reply_text("🚫 **Access Denied.**\nAapko command use karne ki permission nahi hai.")

    if len(message.command) < 2:
        return await message.reply_text(f"❌ **Data missing!**\nSahi format use karein: `/{message.command[0]} [value]`")

    status = await message.reply_text("🔍 **Fetching Details... Please wait.**")

    try:
        try:
            sent_req = await client.send_message(TARGET_BOT, message.text)
        except Exception as e:
            return await status.edit(f"❌ **Target Bot Error:** Pata lagao ki kya aapne target bot ko kabhi /start kiya hai ya nahi.\nError: {e}")

        target_response = None

        for _ in range(30): 
            await asyncio.sleep(2)
            async for log in client.get_chat_history(TARGET_BOT, limit=3):
                if log.id > sent_req.id:
                    text_content = (log.text or log.caption or "").lower()

                    ignore_words = ["wait", "searching", "processing", "loading", "fetching", "scanning"]
                    if any(word in text_content for word in ignore_words) and not log.document:
                        continue 

                    target_response = log
                    break
            if target_response: break

        if not target_response:
            return await status.edit("❌ **Timeout:** Target bot ne time par result nahi diya. Phir se try karein.")

        raw_text = ""
        if target_response.document:
            await status.edit("📂 **Downloading Result File...**")
            path = await client.download_media(target_response)
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                raw_text = f.read()
            os.remove(path)
        else:
            raw_text = target_response.text or target_response.caption or ""

        if not raw_text or len(raw_text.strip()) < 2:
            return await status.edit("❌ **No Data Found or Invalid Data.**")

        clean_output = re.sub(r"⚡ Designed.*|@\w+", "", raw_text).strip()

        if "{" in clean_output:
            final_msg = f"```json\n{clean_output}\n```\n\n⚡ **{BOT_NAME.upper()}**"
        else:
            final_msg = f"**Result:**\n`{clean_output}`\n\n⚡ **{BOT_NAME.upper()}**"

        await status.delete()

        if len(final_msg) > 4000:
            sent_msgs = []
            for i in range(0, len(final_msg), 4000):
                msg = await message.reply_text(final_msg[i:i+4000])
                sent_msgs.append(msg)
                await asyncio.sleep(1)

            await asyncio.sleep(60)
            for m in sent_msgs:
                try: await m.delete()
                except: pass
        else:
            sent = await message.reply_text(final_msg)
            await asyncio.sleep(60)
            try: await sent.delete()
            except: pass

    except Exception as e:
        try:
            await status.edit(f"❌ **System Error:** {str(e)}")
        except:
            await message.reply_text(f"❌ **System Error:** {str(e)}")

# --- BOT START KARNE KA PROCESS ---
async def main():
    Thread(target=run_web, daemon=True).start()
    await app.start()
    print(f"✅ {BOT_NAME.upper()} IS ONLINE AND READY")
    await idle()

if __name__ == "__main__":
    loop.run_until_complete(main())