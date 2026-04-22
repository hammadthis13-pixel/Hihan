import asyncio
import re
import httpx
from bs4 import BeautifulSoup
import time
import json
import os
import traceback
from urllib.parse import urljoin
from datetime import datetime, timedelta

# Telegram libraries
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

BOT_START_TIME = time.time() # For Uptime feature
sent_messages = set()
# --- Configuration (Fill in your details) ---

# Your Telegram Bot Token here
YOUR_BOT_TOKEN = "8361155340:AAEPTN9N-BcsOb1qjL6stn_bPHaBRgZGpnw"

# Admin IDs
ADMIN_CHAT_IDS =["7847937078", "7847937078"]

# Owner Settings
OWNER_TELEGRAM_LINK = "https://t.me/AmmarDevx"

# Files for saving data
STATE_FILE = "processed_sms_ids.json"
CHAT_IDS_FILE = "chat_ids.json"
GROUP_LINKS_FILE = "group_links.json"
USERS_FILE = "all_users.json"
GRANTED_NUMBERS_FILE = "granted_chats.json"
NUMBERS_DIR = "numbers_data"

# --- NEW DATA FILES FOR NUMBER APIs ---
PROCESSED_API_NUMS_FILE = "processed_api_nums.json"
NUMBERS_GROUP_FILE = "numbers_group.json"
PENDING_NUMS_FILE = "pending_numbers.json" # To store until they reach 100

INITIAL_CHAT_IDS =["-1003030778414"]

# SMS APIs Config
API_URLS =[
    "https://kami-api-production-40eb.up.railway.app/api/np?type=sms",
    "https://kami-api-production-40eb.up.railway.app/api/np1?type=sms",
    "https://kami-api1-production.up.railway.app/api/msi?type=sms",
    "https://kami-api1-production.up.railway.app/api/ts?type=sms",
    "https://kami-api1-production.up.railway.app/api/ch?type=sms",
    "https://kami-api1-production.up.railway.app/api/roxy?type=sms",
    "https://kami-api1-production.up.railway.app/api/hs?type=sms",
    "https://kami-api1-production.up.railway.app/api/goat?type=sms"
]

# --- NEW NUMBERS APIs CONFIG ---
NUMBERS_API_URLS =[
    "https://kami-api-production-40eb.up.railway.app/api/np?type=numbers",
    "https://kami-api-production-40eb.up.railway.app/api/np1?type=numbers",
    "https://kami-api1-production.up.railway.app/api/msi?type=numbers",
    "https://kami-api1-production.up.railway.app/api/ts?type=numbers",
    "https://kami-api1-production.up.railway.app/api/ch?type=numbers",
    "https://kami-api1-production.up.railway.app/api/roxy?type=numbers",
    "https://kami-api1-production.up.railway.app/api/hs?type=numbers",
    "https://kami-api1-production.up.railway.app/api/goat?type=numbers"
]

POLLING_INTERVAL_SECONDS = 5

if not os.path.exists(NUMBERS_DIR):
    os.makedirs(NUMBERS_DIR)

COUNTRY_FLAGS = {
"Afghanistan": "🇦🇫", "Albania": "🇦🇱", "Algeria": "🇩🇿", "Andorra": "🇦🇩", "Angola": "🇦🇴",
"Argentina": "🇦🇷", "Armenia": "🇦🇲", "Australia": "🇦🇺", "Austria": "🇦🇹", "Azerbaijan": "🇦🇿",
"Bahrain": "🇧🇭", "Bangladesh": "🇧🇩", "Belarus": "🇧🇾", "Belgium": "🇧🇪", "Benin": "🇧🇯",
"Bhutan": "🇧🇹", "Bolivia": "🇧🇴", "Brazil": "🇧🇷", "Bulgaria": "🇧🇬", "Burkina Faso": "🇧🇫",
"Cambodia": "🇰🇭", "Cameroon": "🇨🇲", "Canada": "🇨🇦", "Chad": "🇹🇩", "Chile": "🇨 ",
"China": "🇨🇳", "Colombia": "🇨🇴", "Congo": "🇨🇬", "Croatia": "🇭🇷", "Cuba": "🇨🇺",
"Cyprus": "🇨🇾", "Czech Republic": "🇨🇿", "Denmark": "🇩🇰", "Egypt": "🇪🇬", "Estonia": "🇪🇪",
"Ethiopia": "🇪🇹", "Finland": "🇫🇮", "France": "🇫🇷", "Gabon": "🇬🇦", "Gambia": "🇬🇲",
"Georgia": "🇬🇪", "Germany": "🇩🇪", "Ghana": "🇬🇭", "Greece": "🇬🇷", "Guatemala": "🇬🇹",
"Guinea": "🇬🇳", "Haiti": "🇭🇹", "Honduras": "🇭🇳", "Hong Kong": "🇭🇰", "Hungary": "🇭🇺",
"Iceland": "🇮🇸", "India": "🇮🇳", "Indonesia": "🇮🇩", "Iran": "🇮🇷", "Iraq": "🇮🇶",
"Ireland": "🇮🇪", "Israel": "🇮🇱", "Italy": "🇮🇹", "IVORY COAST": "🇨🇮", "Ivory Coast": "🇨🇮", "Jamaica": "🇯🇲",
"Japan": "🇯🇵", "Jordan": "🇯🇴", "Kazakhstan": "🇰🇿", "Kenya": "🇰🇪", "Kuwait": "🇰🇼",
"Kyrgyzstan": "🇰🇬", "Laos": "🇱🇦", "Latvia": "🇱🇻", "Lebanon": "🇱🇧", "Liberia": "🇱🇷",
"Libya": "🇱🇾", "Lithuania": "🇱🇹", "Luxembourg": "🇱🇺", "Madagascar": "🇲🇬", "Malaysia": "🇲🇾",
"Mali": "🇲🇱", "Malta": "🇲🇹", "Mexico": "🇲🇽", "Moldova": "🇲🇩", "Monaco": "🇲🇨",
"Mongolia": "🇲🇳", "Montenegro": "🇲🇪", "Morocco": "🇲🇦", "Mozambique": "🇲🇿", "Myanmar": "🇲🇲",
"Namibia": "🇳🇦", "Nepal": "🇳🇵", "Netherlands": "🇳🇱", "New Zealand": "🇳🇿", "Nicaragua": "🇳🇮",
"Niger": "🇳🇪", "Nigeria": "🇳🇬", "North Korea": "🇰🇵", "North Macedonia": "🇲🇰", "Norway": "🇳🇴",
"Oman": "🇴🇲", "Pakistan": "🇵🇰", "Panama": "🇵🇦", "Paraguay": "🇵🇾", "Peru": "🇵🇪",
"Philippines": "🇵🇭", "Poland": "🇵🇱", "Portugal": "🇵🇹", "Qatar": "🇶🇦", "Romania": "🇷🇴",
"Russia": "🇷🇺", "Rwanda": "🇷🇼", "Saudi Arabia": "🇸🇦", "Senegal": "🇸🇳", "Serbia": "🇷🇸",
"Sierra Leone": "🇸🇱", "Singapore": "🇸🇬", "Slovakia": "🇸🇰", "Slovenia": "🇸🇮", "Somalia": "🇸🇴",
"South Africa": "🇿🇦", "South Korea": "🇰🇷", "Spain": "🇪🇸", "Sri Lanka": "🇱🇰", "Sudan": "🇸🇩",
"Sweden": "🇸🇪", "Switzerland": "🇨🇭", "Syria": "🇸🇾", "Taiwan": "🇹🇼", "Tajikistan": "🇹🇯",
"Tanzania": "🇹🇿", "Thailand": "🇹🇭", "TOGO": "🇹🇬", "Tunisia": "🇹🇳", "Turkey": "🇹🇷",
"Turkmenistan": "🇹🇲", "Uganda": "🇺🇬", "Ukraine": "🇺🇦", "United Arab Emirates": "🇦🇪", "United Kingdom": "🇬🇧",
"United States": "🇺🇸", "Uruguay": "🇺🇾", "Uzbekistan": "🇺🇿", "Venezuela": "🇻🇪", "Vietnam": "🇻🇳",
"Yemen": "🇾🇪", "Zambia": "🇿🇲", "Zimbabwe": "🇿🇼", "Unknown Country": "🏴‍☠️",
"PapuaNewGuinea": "🇵🇬", "Oman": "🇴🇲"
}

SERVICE_KEYWORDS = {
"Facebook": ["facebook"], "Google":["google", "gmail"], "WhatsApp": ["whatsapp"],
"Telegram":["telegram"], "Instagram":["instagram", "igme"], "Amazon": ["amazon"],
"Netflix": ["netflix"], "LinkedIn": ["linkedin"], "Microsoft": ["microsoft", "outlook", "live.com"],
"Apple":["apple", "icloud"], "Twitter": ["twitter"], "Snapchat": ["snapchat"],
"TikTok":["tiktok"], "Discord":["discord"], "Signal": ["signal"], "Viber": ["viber"],
"IMO": ["imo"], "PayPal":["paypal"], "Binance": ["binance"], "Uber":["uber"],
"Bolt":["bolt"], "Airbnb": ["airbnb"], "Yahoo": ["yahoo"], "Steam":["steam"],
"Blizzard":["blizzard"], "Foodpanda": ["foodpanda"], "Pathao":["pathao"],
"Messenger":["messenger", "meta"], "Gmail": ["gmail", "google"], "YouTube":["youtube", "google"],
"X":["x", "twitter"], "eBay": ["ebay"], "AliExpress":["aliexpress"], "Alibaba": ["alibaba"],
"Flipkart": ["flipkart"], "Outlook":["outlook", "microsoft"], "Skype":["skype", "microsoft"],
"Spotify":["spotify"], "iCloud":["icloud", "apple"], "Stripe":["stripe"],
"Cash App":["cash app", "square cash"], "Venmo":["venmo"], "Zelle": ["zelle"],
"Wise": ["wise", "transferwise"], "Coinbase":["coinbase"], "KuCoin": ["kucoin"],
"Bybit":["bybit"], "OKX":["okx"], "Huobi": ["huobi"], "Kraken": ["kraken"],
"MetaMask":["metamask"], "Epic Games": ["epic games", "epicgames"],
"PlayStation":["playstation", "psn"], "Xbox": ["xbox", "microsoft"],
"Twitch":["twitch"], "Reddit": ["reddit"], "ProtonMail": ["protonmail", "proton"],
"Zoho":["zoho"], "Quora":["quora"], "StackOverflow": ["stackoverflow"],
"Indeed": ["indeed"], "Upwork":["upwork"], "Fiverr":["fiverr"], "Glassdoor": ["glassdoor"],
"Booking.com":["booking.com", "booking"], "Careem": ["careem"], "Swiggy":["swiggy"],
"Zomato": ["zomato"], "McDonald's":["mcdonalds", "mcdonald's"], "KFC": ["kfc"],
"Nike":["nike"], "Adidas": ["adidas"], "Shein": ["shein"], "OnlyFans": ["onlyfans"],
"Tinder":["tinder"], "Bumble": ["bumble"], "Grindr":["grindr"], "Line":["line"],
"WeChat": ["wechat"], "VK":["vk", "vkontakte"], "Unknown": ["unknown"]
}

SERVICE_EMOJIS = {
"Telegram": "📩", "WhatsApp": "🟢", "Facebook": "📘", "Instagram": "📸", "Messenger": "💬",
"Google": "🔍", "Gmail": "✉️", "YouTube": "▶️", "Twitter": "🐦", "X": "❌",
"TikTok": "🎵", "Snapchat": "👻", "Amazon": "🛒", "eBay": "📦", "AliExpress": "📦",
"Alibaba": "🏭", "Flipkart": "📦", "Microsoft": "🪟", "Outlook": "📧", "Skype": "📞",
"Netflix": "🎬", "Spotify": "🎶", "Apple": "🍏", "iCloud": "☁️", "PayPal": "💰",
"Stripe": "💳", "Cash App": "💵", "Venmo": "💸", "Zelle": "🏦", "Wise": "🌐",
"Binance": "🪙", "Coinbase": "🪙", "KuCoin": "🪙", "Bybit": "📈", "OKX": "🟠",
"Huobi": "🔥", "Kraken": "🐙", "MetaMask": "🦊", "Discord": "🗨️", "Steam": "🎮",
"Epic Games": "🕹️", "PlayStation": "🎮", "Xbox": "🎮", "Twitch": "📺", "Reddit": "👽",
"Yahoo": "🟣", "ProtonMail": "🔐", "Zoho": "📬", "Quora": "❓", "StackOverflow": "🧑‍💻",
"LinkedIn": "💼", "Indeed": "📋", "Upwork": "🧑‍💻", "Fiverr": "💻", "Glassdoor": "🔎",
"Airbnb": "🏠", "Booking.com": "🛏️", "Uber": "🚗", "Lyft": "🚕", "Bolt": "🚖",
"Careem": "🚗", "Swiggy": "🍔", "Zomato": "🍽️", "Foodpanda": "🍱",
"McDonald's": "🍟", "KFC": "🍗", "Nike": "👟", "Adidas": "👟", "Shein": "👗",
"OnlyFans": "🔞", "Tinder": "🔥", "Bumble": "🐝", "Grindr": "😈", "Signal": "🔐",
"Viber": "📞", "Line": "💬", "WeChat": "💬", "VK": "🌐", "Unknown": "❓"
}

def get_unauthorized_markup(): return InlineKeyboardMarkup([[InlineKeyboardButton("Contact Owner", url=OWNER_TELEGRAM_LINK)]])
def load_json(file_path, default):
    if not os.path.exists(file_path): return default
    try:
        with open(file_path, 'r') as f: return json.load(f)
    except: return default
def save_json(file_path, data):
    with open(file_path, 'w') as f: json.dump(data, f, indent=4)
def escape_markdown(text):
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', str(text))

def get_admin_keyboard():
    keyboard =[
        [KeyboardButton("📜 List Chats"), KeyboardButton("📱 Numbers Menu")],[KeyboardButton("➕ Add Chat"), KeyboardButton("➖ Remove Chat")],[KeyboardButton("🔑 Grant Access"), KeyboardButton("🚫 Revoke Access")], 
        [KeyboardButton("📢 Broadcast"), KeyboardButton("🔗 Set Links")],[KeyboardButton("👀 View API Numbers"), KeyboardButton("⚙️ Set Num Group")],
        [KeyboardButton("📊 System Status")] # NEW ADMIN DASHBOARD FEATURE
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_user_keyboard(): return ReplyKeyboardMarkup([[KeyboardButton("📱 Available Numbers")]], resize_keyboard=True)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user, user_id, chat_id = update.message.from_user, str(update.message.from_user.id), str(update.effective_chat.id)
    users = load_json(USERS_FILE, {})  
    if user_id not in users:  
        users[user_id] = user.username or user.first_name  
        save_json(USERS_FILE, users)  
        for admin in ADMIN_CHAT_IDS:  
            try: await context.bot.send_message(chat_id=admin, text=f"🚨 *New User Started the Bot!*\n\n👤 *Name:* {user.first_name}\n🆔 *ID:* `{user_id}`\n🔗 *Username:* @{user.username or 'None'}", parse_mode='Markdown')  
            except Exception: pass  

    if user_id in ADMIN_CHAT_IDS: await update.message.reply_text("👑 *Welcome Admin!*\n\nUse the buttons below to manage the bot.", parse_mode="Markdown", reply_markup=get_admin_keyboard())  
    else:  
        granted_chats = load_json(GRANTED_NUMBERS_FILE,[])  
        if chat_id in granted_chats or user_id in granted_chats: await update.message.reply_text("Welcome! You have access to our numbers database.", reply_markup=get_user_keyboard())  
        else: await update.message.reply_text("SORRY YOU ARE NOT AUTHIRIZED TO USE TSIS BOT CONTACT OWNER", reply_markup=get_unauthorized_markup())

async def handle_button_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text, user_id, chat_id = update.message.text, str(update.message.from_user.id), str(update.message.chat.id)
    is_admin, granted_chats = user_id in ADMIN_CHAT_IDS, load_json(GRANTED_NUMBERS_FILE,[])

    if text == "📜 List Chats" and is_admin: await list_chats_command(update, context)
    elif (text == "📱 Numbers Menu" and is_admin) or (text == "📱 Available Numbers" and (user_id in granted_chats or chat_id in granted_chats)): await send_numbers_menu(update, context, chat_id)
    elif text == "➕ Add Chat" and is_admin: await update.message.reply_text("✏️ `/add_chat <chat_id>`", parse_mode="Markdown")
    elif text == "➖ Remove Chat" and is_admin: await update.message.reply_text("✏️ `/remove_chat <chat_id>`", parse_mode="Markdown")
    elif text == "🔑 Grant Access" and is_admin: await update.message.reply_text("✏️ `/grant_numbers <chat_id>`", parse_mode="Markdown")
    elif text == "🚫 Revoke Access" and is_admin: await update.message.reply_text("✏️ `/revoke_numbers <chat_id>`", parse_mode="Markdown")
    elif text == "📢 Broadcast" and is_admin: await update.message.reply_text("✏️ `/broadcast Your Message Here`", parse_mode="Markdown")
    elif text == "🔗 Set Links" and is_admin: await update.message.reply_text("✏️ `/set_links <chat_id> <main_url> <number_url>`", parse_mode="Markdown")
    elif text == "⚙️ Set Num Group" and is_admin: await update.message.reply_text("✏️ `/set_num_chat <chat_id>`\n\n_Is group me list ban kar jayegi API wale naye numbers ki._", parse_mode="Markdown")
    elif text == "👀 View API Numbers" and is_admin:
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🆕 Latest 50 Numbers", callback_data="view_api_nums_latest")],[InlineKeyboardButton("📂 All / Old Numbers", callback_data="view_api_nums_old")]])
        await update.message.reply_text("👀 *API Numbers View Panel*\n\nChoose what you want to see:", parse_mode="Markdown", reply_markup=kb)
    elif text == "📊 System Status" and is_admin:
        uptime_seconds = int(time.time() - BOT_START_TIME)
        uptime_str = str(timedelta(seconds=uptime_seconds))
        users_count = len(load_json(USERS_FILE, {}))
        sms_count = len(load_json(STATE_FILE,[]))
        api_nums_count = len(load_json(PROCESSED_API_NUMS_FILE,[]))
        
        pending = load_json(PENDING_NUMS_FILE, {})
        pending_total = sum(len(v) for v in pending.values())
        target = load_json(NUMBERS_GROUP_FILE, {}).get("target_chat", "Not Set (Using Default)")
        
        msg = (
            f"📊 *VIP System Dashboard*\n\n"
            f"⏱ *Bot Uptime:* `{uptime_str}`\n"
            f"👥 *Total Bot Users:* `{users_count}`\n"
            f"📨 *Total SMS Processed:* `{sms_count}`\n"
            f"📱 *Total Numbers Fetched:* `{api_nums_count}`\n"
            f"⏳ *Pending Numbers Queue:* `{pending_total}` _(Waiting for 100)_\n"
            f"🎯 *Auto-Send Target Group:* `{target}`"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")

async def set_num_chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.message.from_user.id) not in ADMIN_CHAT_IDS: return
    if not context.args: 
        await update.message.reply_text("❌ Usage: `/set_num_chat <chat_id>`", parse_mode="Markdown")
        return
    chat_id = context.args[0]
    save_json(NUMBERS_GROUP_FILE, {"target_chat": chat_id})
    await update.message.reply_text(f"✅ Success! Target group for new API numbers set to `{chat_id}`", parse_mode="Markdown")

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.message.from_user.id) not in ADMIN_CHAT_IDS: return
    msg = " ".join(context.args)  
    if not msg:  
        await update.message.reply_text("❌ Usage: `/broadcast Your message here`", parse_mode='Markdown')  
        return  
    users, count = load_json(USERS_FILE, {}), 0  
    await update.message.reply_text("⏳ Broadcasting message...")  
    for uid in users:  
        try:  
            await context.bot.send_message(chat_id=uid, text=f"📢 *Message from Admin:*\n\n{msg}", parse_mode='Markdown')  
            count += 1; await asyncio.sleep(0.05) 
        except Exception: pass  
    await update.message.reply_text(f"✅ Broadcast successfully sent to {count} users!")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.message.from_user.id) not in ADMIN_CHAT_IDS: return
    doc = update.message.document
    if not doc.file_name.endswith('.txt'): return
    caption = update.message.caption or ""  
    if caption.startswith("/upload_numbers") and len(caption.split(" ", 1)) > 1:  
        await process_number_file(update, context, doc, caption.split(" ", 1)[1].strip()); return  
    await update.message.reply_text("📁 File received!\nReply with: `/upload_numbers <CountryName>`", parse_mode='Markdown')

async def upload_numbers_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.message.from_user.id) not in ADMIN_CHAT_IDS: return
    if not update.message.reply_to_message or not update.message.reply_to_message.document: await update.message.reply_text("❌ Please reply to a .txt file."); return  
    if not context.args: await update.message.reply_text("❌ Example: `/upload_numbers Pakistan`", parse_mode='Markdown'); return  
    await process_number_file(update, context, update.message.reply_to_message.document, " ".join(context.args))

async def process_number_file(update, context, doc, country):
    file, file_path = await context.bot.get_file(doc.file_id), os.path.join(NUMBERS_DIR, f"{country}.txt")
    await file.download_to_drive(file_path)
    try:  
        with open(file_path, 'r', encoding='utf-8') as f: count = len(f.readlines())  
        await update.message.reply_text(f"✅ Saved **{count} numbers** for **{country}**!", parse_mode='Markdown')  
    except Exception as e: await update.message.reply_text(f"⚠️ Error reading line count: {e}")

async def grant_numbers_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.message.from_user.id) not in ADMIN_CHAT_IDS: return
    if not context.args: return
    chat_id, granted = context.args[0], load_json(GRANTED_NUMBERS_FILE,[])  
    if chat_id not in granted: granted.append(chat_id); save_json(GRANTED_NUMBERS_FILE, granted)  
    await update.message.reply_text(f"✅ Access granted to `{chat_id}`.", parse_mode='Markdown')

async def revoke_numbers_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.message.from_user.id) not in ADMIN_CHAT_IDS: return
    if not context.args: return
    chat_id, granted = context.args[0], load_json(GRANTED_NUMBERS_FILE,[])
    if chat_id in granted: granted.remove(chat_id); save_json(GRANTED_NUMBERS_FILE, granted)
    await update.message.reply_text(f"🚫 Access revoked for {chat_id}.", parse_mode='Markdown')

async def numbers_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id, user_id, granted = str(update.effective_chat.id), str(update.effective_user.id), load_json(GRANTED_NUMBERS_FILE,[])
    if chat_id not in granted and user_id not in granted and user_id not in ADMIN_CHAT_IDS:  
        await update.message.reply_text("Contact owner for access.", reply_markup=get_unauthorized_markup()); return  
    await send_numbers_menu(update, context, update.message.chat_id)

async def send_numbers_menu(update, context, target_chat_id):
    files =[f for f in os.listdir(NUMBERS_DIR) if f.endswith('.txt')]
    if not files: await context.bot.send_message(chat_id=target_chat_id, text="📭 No numbers available."); return
    keyboard =[]  
    for file in files:  
        country = file.replace('.txt', '')  
        with open(os.path.join(NUMBERS_DIR, file), 'r', encoding='utf-8', errors='ignore') as f: count = len(f.readlines())  
        keyboard.append([InlineKeyboardButton(f"🌍 {country} ({count} numbers)", callback_data=f"getnum_{country}")])  
    await context.bot.send_message(chat_id=target_chat_id, text="📋 *Select country:*", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query, user_id, chat_id = update.callback_query, str(update.callback_query.from_user.id), str(update.callback_query.message.chat.id)
    await query.answer()  
    
    if query.data.startswith("view_api_nums_"):
        if user_id not in ADMIN_CHAT_IDS: return
        mode = query.data.split("_")[3]
        processed_nums = load_json(PROCESSED_API_NUMS_FILE,[])
        if not processed_nums:
            await context.bot.send_message(chat_id=chat_id, text="📭 No API numbers fetched yet. APIs are being checked in the background.")
            return
            
        if mode == "latest":
            nums_to_show = processed_nums[-50:]
            msg = f"🆕 *Latest API Numbers ({len(nums_to_show)}):*\n\n"
            for n in reversed(nums_to_show):
                msg += f"📱 `{n}`\n"
            await context.bot.send_message(chat_id=chat_id, text=msg, parse_mode="Markdown")
            
        elif mode == "old":
            file_path = "all_fetched_api_numbers.txt"
            with open(file_path, "w", encoding="utf-8") as f:
                for n in reversed(processed_nums):
                    f.write(f"{n}\n")
            with open(file_path, "rb") as f:
                await context.bot.send_document(
                    chat_id=chat_id, 
                    document=f, 
                    filename="All_API_Numbers.txt",
                    caption=f"📂 Total Fetched API Numbers: **{len(processed_nums)}**", 
                    parse_mode="Markdown"
                )
            os.remove(file_path)
        return

    if query.data == "show_numbers_menu": await send_numbers_menu(update, context, chat_id); return  
    
    if query.data.startswith("getnum_"):  
        granted = load_json(GRANTED_NUMBERS_FILE,[])  
        if chat_id not in granted and user_id not in granted and user_id not in ADMIN_CHAT_IDS: await context.bot.send_message(chat_id=chat_id, text="🚫 No permission."); return  
        country = query.data.split("_", 1)[1]  
        file_path = os.path.join(NUMBERS_DIR, f"{country}.txt")  
        if os.path.exists(file_path):  
            with open(file_path, 'rb') as f: await context.bot.send_document(chat_id=chat_id, document=f, filename=f"{country}_Numbers.txt", caption=f"✅ Numbers for **{country}**!", parse_mode='Markdown')  
        else: await context.bot.send_message(chat_id=chat_id, text="❌ File no longer available.")

async def add_chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.message.from_user.id) not in ADMIN_CHAT_IDS: return
    try:
        new_chat_id, chat_ids = context.args[0], load_json(CHAT_IDS_FILE, INITIAL_CHAT_IDS)
        if new_chat_id not in chat_ids: chat_ids.append(new_chat_id); save_json(CHAT_IDS_FILE, chat_ids); await update.message.reply_text(f"✅ Chat ID {new_chat_id} added.")
        else: await update.message.reply_text("⚠️ Already in list.")
    except IndexError: pass

async def remove_chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.message.from_user.id) not in ADMIN_CHAT_IDS: return
    try:
        chat_ids = load_json(CHAT_IDS_FILE, INITIAL_CHAT_IDS)
        if context.args[0] in chat_ids: chat_ids.remove(context.args[0]); save_json(CHAT_IDS_FILE, chat_ids); await update.message.reply_text(f"✅ Chat ID removed.")
    except IndexError: pass

async def list_chats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.message.from_user.id) not in ADMIN_CHAT_IDS: return
    chat_ids = load_json(CHAT_IDS_FILE, INITIAL_CHAT_IDS)
    num_group = load_json(NUMBERS_GROUP_FILE, {}).get("target_chat", "Not Set")
    
    text = "📜 *Registered SMS Chat IDs:*\n" + "\n".join(map(str, chat_ids)) + "\n\n"
    text += f"⚙️ *Numbers Target Group:* `{num_group}`"
    await update.message.reply_text(text, parse_mode="Markdown")

async def set_links_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) not in ADMIN_CHAT_IDS: return 
    if len(context.args) < 3: return 
    target_chat_id, links = context.args[0], load_json(GROUP_LINKS_FILE, {})  
    links[str(target_chat_id)] = {"main": context.args[1], "number": context.args[2]}; save_json(GROUP_LINKS_FILE, links)  
    await update.message.reply_text(f"✅ Buttons updated for `{target_chat_id}`!", parse_mode='Markdown')

# =================================================================
# FIXED API FETCHING LOGIC (SMS)
# =================================================================

async def fetch_sms_from_apis(client: httpx.AsyncClient):
    all_messages =[]
    for url in API_URLS:
        try:
            res = await client.get(url, timeout=10.0)
            if res.status_code != 200: continue
            try: data = res.json()
            except Exception: continue
                
            messages_list =[]
            if isinstance(data, list): messages_list = data
            elif isinstance(data, dict):
                for key in["data", "messages", "sms", "items", "records", "result", "list", "aaData"]:
                    if key in data and isinstance(data[key], list):
                        messages_list = data[key]
                        break
                if not messages_list:
                    for key, value in data.items():
                        if isinstance(value, list): 
                            messages_list = value
                            break
            if not messages_list: continue

            for item in messages_list:
                phone_number = "N/A"
                sms_text = ""
                date_str = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                country_name = "Unknown Country"

                if isinstance(item, list) and len(item) >= 5:
                    if str(item[0]) == '0,0,0,0' or not str(item[2]).strip() or not str(item[4]).strip(): continue
                    date_str = str(item[0])
                    country_raw = str(item[1])
                    phone_number = str(item[2])
                    sms_text = str(item[4])
                    country_name = country_raw.split('-')[0].strip() if '-' in country_raw else country_raw.split(' ')[0].strip()

                elif isinstance(item, dict):
                    for k in['number', 'phone', 'phone_number', 'sender']:
                        if k in item and item[k]: phone_number = str(item[k]); break
                    for k in['sms', 'message', 'full_sms', 'text', 'msg', 'body', 'content']:
                        if k in item and item[k]: sms_text = str(item[k]); break
                    if not sms_text or sms_text.lower() == 'none': continue
                    date_str = str(item.get('time', item.get('date', date_str)))
                    country_name = str(item.get('country', country_name))
                else: continue

                unique_id = f"{phone_number}-{sms_text}"
                if isinstance(item, dict) and 'id' in item: unique_id = str(item['id'])

                service = "Unknown"  
                lower_sms_text = sms_text.lower()  
                for service_name, kw_list in SERVICE_KEYWORDS.items():  
                    if any(kw in lower_sms_text for kw in kw_list):  
                        service = service_name; break  
                            
                code_match = re.search(r'(\d{3}-\d{3})', sms_text) or re.search(r'\b(\d{4,8})\b', sms_text)  
                code = "N/A"
                if isinstance(item, dict) and item.get('code'): code = str(item['code'])
                elif code_match: code = code_match.group(1)

                clean_country = country_name
                for known_country in COUNTRY_FLAGS.keys():
                    if known_country.lower() in country_name.lower():
                        clean_country = known_country; break

                flag = COUNTRY_FLAGS.get(clean_country, "🏴‍☠️")  

                all_messages.append({  
                    "id": unique_id, "time": date_str, "number": phone_number,   
                    "country": clean_country, "flag": flag, "service": service,   
                    "code": code, "full_sms": sms_text  
                })
        except Exception as e: continue
    return all_messages

async def send_telegram_message(context: ContextTypes.DEFAULT_TYPE, chat_id: str, msg: dict):
    msg_id = f"{msg['number']}_{msg['code']}"
    if msg_id in sent_messages: return False
    sent_messages.add(msg_id)

    try:
        service_emoji = SERVICE_EMOJIS.get(msg['service'], '✨')
        full_message = (
            f"✅ *Verification Code Received*\n\n"
            f"🏆 *{escape_markdown(msg['service'])}* {service_emoji}\n"
            f" ╰ 🔑 *Code:* `{escape_markdown(msg['code'])}`\n"
            f" ╰ 📱 *Phone:* `{escape_markdown(msg['number'])}`\n"
            f" ╰ 🌎 *Geo:* {escape_markdown(msg['country'])} {msg['flag']}\n\n"
            f"📨 *Incoming Message:*\n"
            f"```\n{escape_markdown(msg['full_sms'])}\n```\n"
            f"⏳ _{escape_markdown(msg['time'])}_"
        )

        group_links = load_json(GROUP_LINKS_FILE, {}).get(str(chat_id), {})
        main_url = group_links.get("main", "https://t.me/ammar_devs")
        num_url = group_links.get("number", "https://t.me/ammar_numbers")

        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Main Channel", url=main_url), InlineKeyboardButton("Number Channel", url=num_url)],[InlineKeyboardButton("Developer", url=OWNER_TELEGRAM_LINK)]
        ])

        await context.bot.send_message(chat_id=chat_id, text=full_message, parse_mode="Markdown", reply_markup=reply_markup)
        return True
    except Exception as e: return False

async def check_sms_job(context: ContextTypes.DEFAULT_TYPE):
    async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
        try:
            messages = await fetch_sms_from_apis(client)
            if not messages: return  
            
            processed_list = load_json(STATE_FILE,[])
            chats = load_json(CHAT_IDS_FILE, INITIAL_CHAT_IDS)  
            
            if len(processed_list) == 0:
                sent_count = 0
                for msg in messages: 
                    processed_list.append(msg["id"])
                    if sent_count < 3:
                        for chat_id in chats: await send_telegram_message(context, chat_id, msg)
                        sent_count += 1
                save_json(STATE_FILE, processed_list[-5000:])
                return

            processed = set(processed_list)
            new_processed = processed_list.copy()
            new_msgs_found = False
            for msg in reversed(messages):  
                if msg["id"] not in processed:  
                    new_msgs_found = True
                    for chat_id in chats: await send_telegram_message(context, chat_id, msg)
                    processed.add(msg["id"])
                    new_processed.append(msg["id"])

            if new_msgs_found: save_json(STATE_FILE, new_processed[-5000:])  
        except Exception as e: pass

# =================================================================
# FIXED API FETCHING LOGIC (ONLY NUMBERS) - WITH TXT FILE EXPORT
# =================================================================

async def fetch_api_numbers_only(client: httpx.AsyncClient):
    extracted_nums =[]
    for url in NUMBERS_API_URLS:
        try:
            res = await client.get(url, timeout=10.0)
            if res.status_code != 200: continue
            try: data = res.json()
            except Exception: continue
                
            messages_list =[]
            if isinstance(data, list): messages_list = data
            elif isinstance(data, dict):
                for key in["data", "numbers", "items", "records", "result", "list", "aaData"]:
                    if key in data and isinstance(data[key], list):
                        messages_list = data[key]
                        break
            if not messages_list: continue

            for item in messages_list:
                phone_number = ""
                country_name = "Unknown Country"

                if isinstance(item, list):
                    for val in item:
                        val_str = str(val).strip()
                        clean_check = val_str.replace(" ", "").replace("-", "")
                        if re.match(r'^\+?\d{7,15}$', clean_check): phone_number = clean_check
                        elif len(val_str) > 2 and not any(c.isdigit() for c in val_str):
                            country_name = val_str.split('-')[0].strip()
                            
                    if not phone_number and len(item) >= 3:
                        country_name = str(item[1]).split('-')[0].strip() if '-' in str(item[1]) else str(item[1]).split(' ')[0].strip()
                        phone_number = str(item[2])

                elif isinstance(item, dict):
                    for k in['number', 'phone', 'phone_number']:
                        if k in item and item[k]: phone_number = str(item[k]); break
                    country_name = str(item.get('country', country_name))
                elif isinstance(item, str): phone_number = item
                    
                if not phone_number or str(phone_number).lower() == 'none': continue

                match = re.search(r'\+?\d{6,15}', str(phone_number))
                if match:
                    clean_number = match.group(0)
                    clean_country = country_name
                    for known_country in COUNTRY_FLAGS.keys():
                        if known_country.lower() in country_name.lower():
                            clean_country = known_country; break
                            
                    extracted_nums.append({"number": clean_number, "country": clean_country})
        except Exception as e: continue
    return extracted_nums

async def check_new_numbers_job(context: ContextTypes.DEFAULT_TYPE):
    # To Ensure file is definitely sent even if target_chat is missing, use default fallback
    target_data = load_json(NUMBERS_GROUP_FILE, {})
    target_chat_id = target_data.get("target_chat")
    if not target_chat_id:
        chat_ids = load_json(CHAT_IDS_FILE, INITIAL_CHAT_IDS)
        target_chat_id = chat_ids[0] if chat_ids else INITIAL_CHAT_IDS[0]

    async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
        try:
            fetched_data = await fetch_api_numbers_only(client)
            if not fetched_data: return
            
            processed = load_json(PROCESSED_API_NUMS_FILE,[])
            processed_set = set(processed)
            is_first_run = len(processed_set) == 0
            
            new_nums = []
            for item in fetched_data:
                num = item["number"]
                if num not in processed_set:
                    new_nums.append(item)
                    processed.append(num)
                    processed_set.add(num)
            
            if not new_nums: return
            
            save_json(PROCESSED_API_NUMS_FILE, processed) 
            
            # --- 1. First Time Bot Run Logic (Send All mix file) ---
            if is_first_run:
                file_name = "All_Numbers_Mix.txt"
                file_path = os.path.join(NUMBERS_DIR, file_name)
                
                with open(file_path, "w", encoding="utf-8") as f:
                    for idx, n in enumerate(new_nums, 1):
                        f.write(f"{idx}. {n['number']} - {n['country'].upper()}\n")
                        
                caption = (
                    f"💎 *ALL COUNTRIES MIX* 🌍 *FRESH UPDATE!* 💎\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"📱 *SERVICE:* WHATSAPP / FACEBOOK \n"
                    f"IMO OTP\n"
                    f"⚡️ *STATUS:* ALL FILES WORKING 🟢\n"
                    f"🚀 *SPEED UP - 🟢 TRAFFIC 🟢 HIGH* 🔥\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"🌎 *COUNTRY:* 🌍 *ALL MIXED*"
                )
                
                try:
                    with open(file_path, "rb") as doc:
                        await context.bot.send_document(chat_id=target_chat_id, document=doc, caption=caption, parse_mode="Markdown")
                except Exception as e:
                    print(f"Failed to send first mix doc: {e}")
                finally:
                    if os.path.exists(file_path): os.remove(file_path)
                return 

            # --- 2. Normal Logic: 100+ Numbers limit Queue ---
            pending = load_json(PENDING_NUMS_FILE, {})
            
            for n in new_nums:
                c = n["country"]
                if c not in pending: pending[c] =[]
                pending[c].append(n["number"])
                
            for c, nums in list(pending.items()):
                if len(nums) >= 100: # Wait until we have 100+ numbers for this country
                    flag = COUNTRY_FLAGS.get(c, "🏴‍☠️")
                    timestamp = datetime.now().strftime("%Y-%m-%dT%H%M%S.000")
                    file_name = f"SMSNumbers-{timestamp}.txt"
                    file_path = os.path.join(NUMBERS_DIR, file_name)
                    
                    with open(file_path, "w", encoding="utf-8") as f:
                        for idx, num in enumerate(nums, 1):
                            f.write(f"{idx}. {num} - {c.upper()}\n")
                            
                    caption = (
                        f"💎 *{c.upper()}* {flag} *FRESH UPDATE!* 💎\n"
                        f"━━━━━━━━━━━━━━━━━━\n"
                        f"📱 *SERVICE:* WHATSAPP / FACEBOOK \n"
                        f"IMO OTP\n"
                        f"⚡️ *STATUS:* ALL FILES WORKING 🟢\n"
                        f"🚀 *SPEED UP - 🟢 TRAFFIC 🟢 HIGH* 🔥\n"
                        f"━━━━━━━━━━━━━━━━━━\n"
                        f"🌎 *COUNTRY:* {flag} *{c.upper()}*"
                    )
                    
                    try:
                        with open(file_path, "rb") as doc:
                            await context.bot.send_document(chat_id=target_chat_id, document=doc, caption=caption, parse_mode="Markdown")
                        pending.pop(c) # Done! Remove this country from pending list
                        await asyncio.sleep(2)
                    except Exception as e:
                        print(f"Failed to send 100+ Numbers List Document: {e}")
                    finally:
                        if os.path.exists(file_path): os.remove(file_path)
                        
            # Save updated pending lists back
            save_json(PENDING_NUMS_FILE, pending)

        except Exception as e:
            print(f"Number Job Error: {e}")

# =================================================================
# MAIN START
# =================================================================

def main():
    print("🚀 Bot starting...")
    application = Application.builder().token(YOUR_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))  
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_button_text))
    application.add_handler(CommandHandler("add_chat", add_chat_command))  
    application.add_handler(CommandHandler("remove_chat", remove_chat_command))  
    application.add_handler(CommandHandler("list_chats", list_chats_command))  
    application.add_handler(CommandHandler("set_links", set_links_command))  
    application.add_handler(CommandHandler("broadcast", broadcast_command))
    application.add_handler(CommandHandler("grant_numbers", grant_numbers_command))  
    application.add_handler(CommandHandler("revoke_numbers", revoke_numbers_command))  
    application.add_handler(CommandHandler("numbers", numbers_command))  
    application.add_handler(CommandHandler("upload_numbers", upload_numbers_command))
    application.add_handler(CommandHandler("set_num_chat", set_num_chat_command))  

    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))  
    application.add_handler(CallbackQueryHandler(button_callback))  

    application.job_queue.run_repeating(
        check_sms_job,
        interval=POLLING_INTERVAL_SECONDS,
        first=1,
        job_kwargs={"max_instances": 3, "misfire_grace_time": 30}
    )
    
    application.job_queue.run_repeating(
        check_new_numbers_job,
        interval=10, 
        first=2,
        job_kwargs={"max_instances": 1, "misfire_grace_time": 30}
    )

    application.run_polling()

if __name__ == "__main__":
    main()