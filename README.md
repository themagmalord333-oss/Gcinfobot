
<div align="center">
<img src="https://i.ibb.co/gZhFNqLP/x.jpg" alt="Bot Logo">
<h1>Telegram Proxy & Data Routing Bot</h1>
<p>
<b>A Pyrogram-based intermediary bot for automated querying, response parsing, and access control.</b>
</p>
<p>Python | Pyrogram | Flask</p>
</div>

## ⚙️ Core Logic & Architecture
This script acts as a middleman between authorized users and a hidden backend target bot. It utilizes a Telegram User Session to automate data retrieval without exposing the underlying target bot to the end-users.

**Execution Flow:**
 1. **Command Interception:** The bot listens for specific trigger commands (e.g., `/num`).
 2. **Access Verification:** Checks if the sender's `user_id` exists in the `AUTHORIZED_USERS` memory list.
 3. **Query Routing:** Forwards the raw query payload to the predefined `TARGET_BOT`.
 4. **Async Polling:** Polls the `TARGET_BOT`'s chat history every 2 seconds (up to 30 iterations/60 seconds), explicitly ignoring transitional states like "waiting", "loading", or "processing".
 5. **Data Extraction & Scrubbing:**
   * If the response is a document, it downloads, reads the UTF-8 text, and deletes the local file.
   * Applies Regex (`re.sub`) to strip external branding, tags, and `@usernames` from the raw text.
 6. **Delivery & Auto-Deletion:** Formats the output (JSON block or Markdown), chunks messages if they exceed Telegram's 4000-character limit, and schedules an automatic `message.delete()` after 60 seconds to clear chat history.

## 🛠 Technical Features
 * **Strict Authorization System:** Only hardcoded `OWNER_ID` and `ADMIN_ID` can execute the `/auth` command to append new users to the active runtime list.
 * **Smart Response Parser:** Handles both standard text replies and `.txt` document uploads from the target bot.
 * **Pagination (Message Splitting):** Automatically chunks large payloads into sequential messages to prevent API `MessageTooLong` exceptions.
 * **Event Loop Management:** Explicitly creates and sets a new asyncio event loop to prevent runtime errors in newer Python environments (3.10+).
 * **Daemon Web Server:** Runs a parallel Flask thread on `0.0.0.0` to bind to cloud provider ports, preventing container suspension.

## 🚀 Setup & Deployment

### 1. Requirements
```bash
pip install pyrogram tgcrypto flask python-dotenv

2. Environment Variables (.env)
The system relies entirely on environment variables for configuration. Create a .env file in the root directory:
PORT=8080
API_ID=1234567
API_HASH="your_api_hash"
SESSION_STRING="your_pyrogram_string_session"
BOT_NAME="ProxyBot"
TARGET_BOT="Target_Bot_Username"
OWNER_ID=123456789
ADMIN_ID=987654321

3. Execution
python main.py

📚 System Commands
Access Control
| Command | Logic |
|---|---|
| /auth [User_ID] | Appends the specified User ID to the AUTHORIZED_USERS list. Only executable by Owner/Admin. |
| /ping | Simple latency and uptime check. |
Data Queries
All commands below follow the same routing logic to the TARGET_BOT.
| Command | Expected Input |
|---|---|
| /num | Mobile Number |
| /vehicle | Vehicle Plate Number |
| /aadhar | UID/Aadhaar Number |
| /familyinfo | UID/Aadhaar Number |
| /vnum | Vehicle Plate Number |
| /tgnum | Telegram User ID |
| /fam / /sms | Target Identifiers |


👨‍💻 Developer & Community
 * Developer: @Smugllers
 * Telegram Group: @MAGMAxRICH
 * GitHub: themagmalord333-oss