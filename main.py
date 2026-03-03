import asyncio

# --- 🔥 CRITICAL FORCE-PATCH FOR PYTHON 3.14 ON RENDER 🔥 ---
def get_or_create_loop():
    try:
        return asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop

asyncio.get_event_loop = get_or_create_loop

# --- NOW IMPORT EVERYTHING ELSE ---
import os
import logging
import json
import re
from threading import Thread
from flask import Flask
from pyrogram import Client, filters, idle

# --- LOGGING ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- WEB SERVER (FOR RENDER/UPTIME) ---
web_app = Flask(__name__)
@web_app.route('/')
def home(): return "🤖 VIP BLUE HAT NETWORK is Running!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)

# --- CONFIGURATION ---
API_ID = 37314366
API_HASH = "bd4c934697e7e91942ac911a5a287b46"
SESSION_STRING = "BQI5Xz4AR_aXPWyOA7MjNKKwcf6LpEGlsd7-Z2NQyejkpu9XpXqVJWYmeG50yWst1lHn7vf8wVmyHl3Evp-rS_CJ61_UbXrimcTdq2VBS9uSvAiNFlJ1HE3eFLy6anVQMyxjvDKJIZMAvRadMDAI1sxhZiRSZDZ0Idv05HRlAELA8f3rBoNEB6ch1BEui3ZTgpx7Tttdsj4EoG-HoRNIlENg5IKwTIhHkH2KZ0i4YmHlTIOnlR7Rjn2l5sZMe2A0aP3_Ffwl7feJODQzBVFw8N2nEhoK7C9jHbyqGq2mWLOWl4_EQm7CIlUJ8QN-g2-ei5oPMzWJREOH1Im0DgFzGz0qnfznIgAAAAFJSgVkAA"

TARGET_BOT = "Backupinfo69_bot"
BOT_NAME = "vipbluehatnetwork"

OWNER_ID = 7762163050
ADMIN_ID = 7727470646

# List to store authorized user IDs
AUTHORIZED_USERS = [OWNER_ID, ADMIN_ID]

app = Client("vip_blue_hat", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

# --- ACCESS CONTROL FILTER ---
async def is_authorized(_, __, message):
    if not message.from_user: return False
    return message.from_user.id in AUTHORIZED_USERS

auth_filter = filters.create(is_authorized)

# --- COMMAND: AUTHENTICATE USER ---
@app.on_message(filters.command("auth") & filters.user([OWNER_ID, ADMIN_ID]))
async def authorize_user(client, message):
    if len(message.command) < 2:
        return await message.reply_text("❌ Usage: `/auth [User_ID]`")
    try:
        user_id = int(message.command[1])
        if user_id not in AUTHORIZED_USERS:
            AUTHORIZED_USERS.append(user_id)
            await message.reply_text(f"✅ User `{user_id}` has been authorized.")
        else:
            await message.reply_text("ℹ️ User is already authorized.")
    except ValueError:
        await message.reply_text("❌ Invalid User ID.")

# --- DASHBOARD / START ---
@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    if message.from_user.id not in AUTHORIZED_USERS:
        return await message.reply_text("🚫 **Access Denied.**\nContact Admin or Owner for permission.")
    
    text = (
        f"🛡️ **Welcome to {BOT_NAME}**\n\n"
        "**Available Commands:**\n"
        "📱 `/num [number]` → Number Details\n"
        "🚗 `/vehicle [Plate]` → Challan And Rc\n"
        "🆔 `/aadhar [UID]` → Aadhaar Info\n"
        "👨‍👩‍👧 `/familyinfo [aadhar]` → Family Tree\n"
        "🔗 `/vnum [Plate]` → Linked Mobile\n"
        "📞 `/tgnum [TG ID]` → User's Mobile\n\n"
        "⚡ **Powered by VIP BLUE HAT NETWORK**"
    )
    await message.reply_text(text)

# --- MAIN LOOKUP LOGIC ---
@app.on_message(filters.command(["num", "vehicle", "aadhar", "familyinfo", "vnum", "tgnum"]) & filters.private & auth_filter)
async def process_lookup(client, message):
    if len(message.command) < 2:
        return await message.reply_text(f"❌ **Data missing!**\nSahi format use karein: `/{message.command[0]} [value]`")

    status = await message.reply_text("🔍 **Fetching Details... Please wait.**")
    
    try:
        # Forward request to target bot
        sent_req = await client.send_message(TARGET_BOT, message.text)
        
        target_response = None
        
        # SMART WAIT LOOP: 60 Seconds Timeout (Wait for ACTUAL response)
        for _ in range(30): 
            await asyncio.sleep(2)
            async for log in client.get_chat_history(TARGET_BOT, limit=2):
                # Check if message is from Target Bot and newer than our request
                if not log.from_user.is_self and log.id > sent_req.id:
                    text_content = (log.text or log.caption or "").lower()
                    
                    # Ignore "Processing" messages sent by the target bot
                    if any(word in text_content for word in ["wait", "searching", "processing", "loading"]):
                        continue 
                        
                    target_response = log
                    break
            if target_response: break

        if not target_response:
            return await status.edit("❌ **Timeout:** Target bot ne koi response nahi diya.")

        # Handle File or Text Result
        raw_text = ""
        if target_response.document:
            path = await client.download_media(target_response)
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                raw_text = f.read()
            os.remove(path)
        else:
            raw_text = target_response.text or target_response.caption or ""

        if not raw_text:
            return await status.edit("❌ **No Data Found or Invalid Format.**")

        # Clean Output (Remove old ads/credits)
        clean_output = re.sub(r"⚡ Designed.*|@\w+", "", raw_text).strip()
        
        # Format properly if it looks like JSON
        if "{" in clean_output:
            final_msg = f"```json\n{clean_output}\n```\n\n⚡ **{BOT_NAME}**"
        else:
            final_msg = f"**Result:**\n`{clean_output}`\n\n⚡ **{BOT_NAME}**"
        
        await status.delete()
        
        # Send result (Split if too long)
        if len(final_msg) > 4000:
            sent_msgs = []
            for i in range(0, len(final_msg), 4000):
                msg = await message.reply_text(final_msg[i:i+4000])
                sent_msgs.append(msg)
                await asyncio.sleep(1)
            # Auto delete large results after 60s
            await asyncio.sleep(60)
            for m in sent_msgs:
                try: await m.delete()
                except: pass
        else:
            sent = await message.reply_text(final_msg)
            # Auto delete result after 60s
            await asyncio.sleep(60)
            try: await sent.delete()
            except: pass

    except Exception as e:
        await status.edit(f"❌ **Error:** {str(e)}")

# --- STARTUP ---
async def main():
    Thread(target=run_web, daemon=True).start()
    await app.start()
    print("✅ VIP BLUE HAT NETWORK IS ONLINE AND READY")
    await idle()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
