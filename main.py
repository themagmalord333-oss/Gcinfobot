import os
import asyncio
import json
import threading
from flask import Flask
from pyrogram import Client, filters, enums
from pyrogram.errors import UserNotParticipant, PeerIdInvalid, ChannelInvalid

# --- 🌐 WEB SERVER (Render Error Fix) ---
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Bot is Running 24/7! 🚀"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host='0.0.0.0', port=port)

t = threading.Thread(target=run_web)
t.daemon = True
t.start()

# --- CONFIGURATION ---
API_ID = 37314366
API_HASH = "bd4c934697e7e91942ac911a5a287b46"

# 👇👇 YAHAN APNA NAYA GENERATE KIYA HUA STRING PASTE KAREIN 👇👇
SESSION_STRING = "BQI5Xz4AQqz9RmhHLzmvF9-Bt6WIN65bdc6IbDerxk8kuuZbVy9dstGTN120mILr9sqR4qxYl-VpJ0GpKxpECmbUqSla0-Y49Lj-ENjxA9np0_hLpVBY6xCw0TWBgetpfMygqv2VVKIHMcDlqXzQUJq4cdAviXxwwFa5C89PcsCt4LKwb45gboSbir8YCmHWy_ob5D7sHthy-5o68JtW68o9lZenYRuEzSZXI8_kFv_RK8NL5cMR2zF1epTDJhV6blnLAuQ1eyMVLI4fOBByo6pvZLYdOFExbxneMKos7sPI6qy4DRLYIN8cWqIl0_38zDbT55t2WEUl3fmsBraSW82Yl9AHNAAAAAFJSgVkAA" 

# 🎯 TARGET SETTINGS
TARGET_BOT_USERNAME = "DeepTraceXBot"
SEARCH_GROUP_ID = -1003426835879 

# --- 🔐 SECURITY SETTINGS ---
ALLOWED_GROUPS = [-1003387459132] 

# Force Sub Channels
FSUB_CONFIG = [
    {"username": "-----", "link": "_________"},
    {"username": "___________", "link": "__________"}
]

app = Client("anysnap_secure_bot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

# --- HELPER: CHECK IF USER JOINED ---
async def check_user_joined(client, user_id):
    missing = False
    for ch in FSUB_CONFIG:
        try:
            member = await client.get_chat_member(ch["username"], user_id)
            if member.status in [enums.ChatMemberStatus.LEFT, enums.ChatMemberStatus.BANNED]:
                missing = True
                break
        except UserNotParticipant:
            missing = True
            break
        except Exception:
            pass 
    return not missing 

# --- DASHBOARD ---
@app.on_message(filters.command(["start", "help", "menu"], prefixes="/") & (filters.private | filters.chat(ALLOWED_GROUPS)))
async def show_dashboard(client, message):
    if not await check_user_joined(client, message.from_user.id):
        return await message.reply_text("🚫 **Access Denied!** Join channels first.")

    text = (
        "📖 **ANYSNAP BOT DASHBOARD**\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "🔍 **Available Commands:**\n"
        "📱 `/num [number]`\n🆔 `/aadhaar [uid]`\n🏢 `/gst [no]`\n"
        "🏦 `/ifsc [code]`\n💰 `/upi [id]`\n💸 `/fam [id]`\n"
        "🚗 `/vehicle [plate]`\n✈️ `/tg [username]`\n"
        "🕵️ `/trace [num]`\n📧 `/gmail [email]`\n\n"
        "**⚠️ Note:** Results auto-delete in 30s.\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "⚡ **Designed & Powered by @MAGMAxRICH**"
    )
    await message.reply_text(text)

# --- MAIN LOGIC ---
@app.on_message(filters.command(["num", "aadhaar", "gst", "ifsc", "upi", "fam", "vehicle", "tg", "trace", "gmail"], prefixes="/") & (filters.private | filters.chat(ALLOWED_GROUPS)))
async def process_request(client, message):
    if not await check_user_joined(client, message.from_user.id):
        return await message.reply_text("🚫 **Access Denied!** Join channels first.")

    if len(message.command) < 2:
        return await message.reply_text(f"❌ **Data Missing!**\nUsage: `/{message.command[0]} <value>`")

    status_msg = await message.reply_text(f"🔍 **Searching via Anysnap...**")
    
    try:
        await client.get_chat(SEARCH_GROUP_ID)
    except Exception as e:
        await status_msg.edit(f"❌ **Bot not in Group!** Please join group `{SEARCH_GROUP_ID}` manually.")
        return

    try:
        sent_req = await client.send_message(SEARCH_GROUP_ID, message.text)
        target_response = None
        
        for attempt in range(20): 
            await asyncio.sleep(2.5) 
            async for log in client.get_chat_history(SEARCH_GROUP_ID, limit=5):
                if log.from_user and log.from_user.username == TARGET_BOT_USERNAME:
                    if log.reply_to_message_id == sent_req.id:
                        text_content = (log.text or log.caption or "").lower()
                        if any(w in text_content for w in ["wait", "processing", "loading"]):
                            await status_msg.edit(f"⏳ **Processing... ({attempt+1})**")
                            break 
                        target_response = log
                        break 
            if target_response: break
        
        if not target_response:
            await status_msg.edit("❌ **Timeout:** No reply received.")
            return

        raw_text = ""
        if target_response.document:
            await status_msg.edit("📂 **Downloading...**")
            file_path = await client.download_media(target_response)
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                raw_text = f.read()
            os.remove(file_path)
        elif target_response.photo:
            raw_text = target_response.caption or ""
        elif target_response.text:
            raw_text = target_response.text

        clean_data_list = []
        for line in raw_text.splitlines():
            line = line.strip()
            if not line: continue 
            if "@" in line or "Designed" in line or "DeepTrace" in line:
                if not any(k in line for k in ["Name", "Number", "Vehicle", "GST", "IFSC", "Email", "Status", "DOB", "Address"]):
                    continue
            clean_data_list.append(line)

        json_data = {
            "status": "success",
            "service": message.command[0],
            "query": " ".join(message.command[1:]),
            "data": clean_data_list,  
            "powered_by": "@MAGMAxRICH"
        }
        
        result_msg = await message.reply_text(f"```json\n{json.dumps(json_data, indent=4, ensure_ascii=False)}\n```")
        await status_msg.delete()
        await asyncio.sleep(30)
        try: await result_msg.delete()
        except: pass 

    except Exception as e:
        await status_msg.edit(f"❌ **Error:** {str(e)}")

print("🚀 Secure ANYSNAP is Live!")
app.run()
