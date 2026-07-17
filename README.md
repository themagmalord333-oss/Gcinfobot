<div align="center">
<img src="[https://i.ibb.co/gZhFNqLP/x.jpg](https://i.ibb.co/gZhFNqLP/x.jpg)" alt="VIP Blue Hat Logo" width="150" height="150" style="border-radius: 50%; box-shadow: 0 0 20px rgba(0, 123, 255, 0.5);">
<h1>🚀 VIP BLUE HAT NETWORK</h1>
<p>
<b>An elite, high-speed OSINT and data-lookup intermediary bot for Telegram.</b>
</p>
Python

Pyrogram

Flask

License
</div>
## ✨ About The Project
**VIP Blue Hat Network** is a highly optimized Telegram automation client built with Pyrogram. It serves as a secure bridge between authorized users and private database bots (Target Bots). By processing commands locally and querying backend services, it delivers lightning-fast OSINT data, vehicle details, and identity lookups with built-in access control and privacy-focused auto-deletion.
## 🚀 Key Features
 * **Strict Access Control:** Features a robust /auth system. Only the Owner and Admins can authorize new users. Unverified users cannot execute lookups.
 * **Seamless Bot-to-Bot Routing:** Intercepts user commands, silently queries a designated TARGET_BOT, and parses the response back to the user cleanly.
 * **Privacy First (Auto-Delete):** Automatically deletes sensitive data after 60 seconds to ensure no digital footprints are left behind in the chat.
 * **Smart Parsing:** Cleans up forwarded text, removes third-party branding/ads, and formats JSON outputs into beautiful markdown blocks.
 * **Cloud-Ready Keep-Alive:** Integrated with a background Flask web server, ensuring 24/7 uptime on platforms like Render, Koyeb, and Heroku.
 * **Long Message Handling:** Automatically splits and delivers large data dumps (over 4000 characters) smoothly.
## 🏗 System Architecture
The system operates as an intelligent middleman:
 1. **User Request:** An authorized user sends a command (e.g., /num 9876543210).
 2. **Silent Query:** The bot forwards the query to the hidden TARGET_BOT using the configured Pyrogram String Session.
 3. **Data Extraction:** The bot waits, filters out "processing" messages, and extracts the final text or document from the target bot.
 4. **Clean Delivery:** The bot scrubs the data of external branding and delivers the clean results to the user, automatically deleting them after 60 seconds.
## 🛠 Installation Guide
 1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/vip-blue-hat.git
   cd vip-blue-hat
   
   ```
 2. **Install dependencies:**
   ```bash
   pip install pyrogram tgcrypto flask python-dotenv
   
   ```
 3. **Configure Environment Variables:**
   Create a .env file in the root directory and add your credentials:
   ```env
   PORT=8080
   API_ID=Your_API_ID
   API_HASH="Your_API_HASH"
   SESSION_STRING="Your_Pyrogram_Session"
   BOT_NAME="vipbluehatnetwork"
   TARGET_BOT="Backupinfo69_bot"
   OWNER_ID=7762163050
   ADMIN_ID=7727470646
   
   ```
 4. **Start the Network:**
   ```bash
   python main.py
   
   ```
## 📚 Commands Reference
### 🔐 Admin & Authorization
| Command | Description | Permission |
|---|---|---|
| /auth [User_ID] | Authorizes a new user to use the bot's lookup commands. | Owner/Admin Only |
| /ping | Checks if the bot is online and responding. | Authorized Users |
### 🔍 OSINT & Data Lookup
| Command | Description |
|---|---|
| /num [number] | Fetches detailed mobile number information. |
| /vehicle [Plate] | Retrieves Vehicle RC and Challan details. |
| /aadhar [UID] | Looks up identity information. |
| /familyinfo [UID] | Generates a family tree/connection map. |
| /vnum [Plate] | Finds the mobile number linked to a vehicle. |
| /tgnum [TG ID] | Extracts the mobile number of a Telegram User ID. |
*(Note: All lookup commands require prior authorization via the /auth command.)*
## 🔒 Security & Privacy Notice
 * **Session Security:** This bot requires a Pyrogram User Session (SESSION_STRING). Do not share your .env file or commit it to public repositories.
 * **Auto-Destruction:** To protect sensitive information, the bot is programmed to automatically delete result messages after 1 minute.
 * **Usage Disclaimer:** This tool is designed for educational, administrative, and authorized OSINT research. Ensure you comply with local data protection and privacy laws when handling identity or vehicle information.
## 📞 Support & Credits
<div align="center">
**Developed for YOU**
Telegram Owner
</div>