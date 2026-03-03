import asyncio

# --- 🔥 CRITICAL FORCE-PATCH FOR PYTHON 3.14 ON RENDER 🔥 ---
# Ye Pyrogram ko hamesha ek valid loop dega aur RuntimeError aane nahi dega.
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
SESSION_STRING = "BQI5Xz4AlbuU3B5b_1PGYQuKw8hHzdc--FupA_5OTNcfpP0x_N-lTGTWVLbCbAyWVNTog5wIynXUFTi9VcsMw3FqX40tzuK7RnLT32Rcw6mdRKfZ3Dnl903ZU-4wVi_EgnE006uHqnoQjzzwlYqAr7N8dvgfDhn4-vTTj-Pvm9tTobzToT_utoHpsV1KrVVjwYNTGIqPbURAcXtrJIIN_JIcCnMoklpe3WdMAF0w-7TEOxpa9RFM-zyVafqKb1OoGGacq-B6jTNDzCtbv7Tz__dNlYkLtVwMaVE_vnOjZjECIT9Sxsc067edG9d6iXr4G0u_wcC4BR7ZpGrf1UHAp8ErefHs0wAAAAFJSgVkAA"

TARGET_BOT = "Backupinfo69_bot"
BOT_NAME = "vipbluehatnetwork"

OWNER_ID = 7762163050
ADMIN_ID = 7727470646

# List to store authorized user IDs
AUTHORIZED_USERS = [OWNER_ID, ADMIN_ID]

# Pyrogram Client Initialization
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
            await message.reply_text("User is already authorized.")
    except ValueError:
        await message.reply_text("Invalid User ID.")

# --- DASHBOARD / START ---
@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    if message.from_user.id not in AUTHORIZED_USERS:
        return await message.reply_text("🚫 **Access Denied.**\nContact Admin or Owner for permission.")
    
    await message.reply_text(
        f"🛡️ **Welcome to {BOT_NAME}**\n\n"
        "Send lookup commands like:\n"
        "`/num [number]`\n`/vehicle [plate]`\n`/aadhar [uid]`"
    )

# --- MAIN LOOKUP LOGIC ---
@app.on_message(filters.command(["num", "vehicle", "aadhar", "familyinfo", "vnum", "fam", "sms"]) & filters.private & auth_filter)
async def process_lookup(client, message):
    if len(message.command) < 2:
        return await message.reply_text("❌ Data missing!")

    status = await message.reply_text("🔍 **Searching Data...**")
    
    try:
        # Forward request to target bot
        sent_req = await client.send_message(TARGET_BOT, message.text)
        
        target_response = None
        for _ in range(20): # 40 seconds timeout
            await asyncio.sleep(2)
            async for log in client.get_chat_history(TARGET_BOT, limit=1):
                if log.id != sent_req.id:
                    target_response = log
                    break
            if target_response: break

        if not target_response:
            return await status.edit("❌ No response from target.")

        # Handle File or Text
        raw_text = ""
        if target_response.document:
            path = await client.download_media(target_response)
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                raw_text = f.read()
            os.remove(path)
        else:
            raw_text = target_response.text or target_response.caption or ""

        # Remove old ads/credits from text
        clean_output = re.sub(r"⚡ Designed.*|@\w+", "", raw_text).strip()

        final_msg = f"```json\n{clean_output}\n```\n\n⚡ **{BOT_NAME}**"
        
        await status.delete()
        sent = await message.reply_text(final_msg)
        
        # Auto delete result after 60 seconds
        await asyncio.sleep(60)
        try:
            await sent.delete()
        except:
            pass

    except Exception as e:
        await status.edit(f"❌ Error: {str(e)}")

# --- STARTUP ---
async def main():
    Thread(target=run_web, daemon=True).start()
    await app.start()
    print("✅ VIP BLUE HAT NETWORK IS ONLINE")
    await idle()

if __name__ == "__main__":
    # Get the loop securely using our patched function
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
