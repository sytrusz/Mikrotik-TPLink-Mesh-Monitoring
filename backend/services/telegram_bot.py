import os
import httpx
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.request import HTTPXRequest
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# MikroTik Credentials for Chat-Ops
MIKROTIK_HOST = os.getenv("MIKROTIK_HOST")
MIKROTIK_USER = os.getenv("MIKROTIK_USER")
MIKROTIK_PASS = os.getenv("MIKROTIK_PASS")
MIKROTIK_BASE_URL = f"http://{MIKROTIK_HOST}/rest"

bot_app = None

telegram_request = HTTPXRequest(
    http_version="1.1", 
    connection_pool_size=4,
    connect_timeout=30.0
)

def is_authorized(chat_id):
    """Checks if the user's chat ID is in the allowed list."""
    if not CHAT_ID: return False
    allowed_ids = [cid.strip() for cid in CHAT_ID.split(',')]
    return str(chat_id) in allowed_ids

async def get_status_message():
    """Generates the current status message string."""
    from main import app_cache
    msg = "🌐 *Current Network Status*\n\n"
    for name, isp in app_cache["isps"].items():
        status_emoji = "🟢" if isp["status"] == "ONLINE" else "🔴"
        msg += f"{status_emoji} *{name.upper()}*: {isp['status']}\n"
        msg += f"   - Latency: {isp['latencyMs']}ms\n"
        msg += f"   - Speed: ↓{isp['rx']} ↑{isp['tx']}\n\n"
    
    msg += f"💻 *Router Health*\n"
    msg += f"   - CPU: {app_cache['router_health']['cpu']}\n"
    msg += f"   - Temp: {app_cache['router_health']['temp']}\n"
    return msg

async def send_notification(text, buttons=None):
    """Sends a push notification to all authorized Telegram users."""
    if not TOKEN or not CHAT_ID:
        return
    
    allowed_ids = [cid.strip() for cid in CHAT_ID.split(',')]
    bot = Bot(token=TOKEN, request=telegram_request)
    
    reply_markup = None
    if buttons:
        keyboard = [[InlineKeyboardButton(b['text'], callback_data=b['callback_data'])] for b in buttons]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
    for cid in allowed_ids:
        try:
            await bot.send_message(chat_id=cid, text=text, reply_markup=reply_markup, parse_mode='Markdown')
        except Exception as e:
            print(f"Telegram notification error for {cid}: {e}")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_chat.id): return
    msg = await get_status_message()
    await update.message.reply_text(msg, parse_mode='Markdown')

async def logs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from main import app_cache
    if not is_authorized(update.effective_chat.id): return

    outages = app_cache.get("outages", [])
    if not outages:
        await update.message.reply_text("✅ No recent outages found.")
        return

    msg = "📜 *Recent Outages*\n\n"
    for o in outages[:3]:
        msg += f"*{o['isp']}* ({o['reason']})\n"
        msg += f"   - Dropped: {o['dropped_at'] or '---'}\n"
        msg += f"   - Recovered: {o['recovered_at'] or 'Ongoing'}\n\n"
    await update.message.reply_text(msg, parse_mode='Markdown')

async def mesh_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from main import app_cache
    if not is_authorized(update.effective_chat.id): return

    mesh = app_cache.get("mesh", {})
    msg = "🏠 *Mesh Network*\n\n"
    for node in mesh.get("nodes", []):
        status = "🟢" if node["online"] else "🔴"
        msg += f"{status} *{node['name']}*\n"
        msg += f"   - Clients: {node['clients']}\n"
        msg += f"   - Speed: ↓{node['rx']} ↑{node['tx']}\n\n"
    await update.message.reply_text(msg, parse_mode='Markdown')

async def manage_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_chat.id): return
    
    # We get interface names from env to create the buttons
    wan1 = os.getenv("MIKROTIK_WAN1_NAME", "ether1")
    wan2 = os.getenv("MIKROTIK_WAN2_NAME", "ether2")
    
    keyboard = [
        [
            InlineKeyboardButton(f"✅ Enable {wan1}", callback_data=f"enable_{wan1}"),
            InlineKeyboardButton(f"❌ Disable {wan1}", callback_data=f"disable_{wan1}")
        ],
        [
            InlineKeyboardButton(f"✅ Enable {wan2}", callback_data=f"enable_{wan2}"),
            InlineKeyboardButton(f"❌ Disable {wan2}", callback_data=f"disable_{wan2}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🎛 *Router Interface Management*\nChoose a port to toggle:", reply_markup=reply_markup, parse_mode='Markdown')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_authorized(update.effective_chat.id): return

    data = query.data
    
    if data.startswith("enable_") or data.startswith("disable_"):
        action = "false" if data.startswith("enable_") else "true"
        action_text = "re-enabled" if action == "false" else "disabled"
        interface_name = data.replace("enable_", "").replace("disable_", "")
        
        try:
            async with httpx.AsyncClient(auth=(MIKROTIK_USER, MIKROTIK_PASS), verify=False) as client:
                resp = await client.patch(
                    f"{MIKROTIK_BASE_URL}/interface/{interface_name}",
                    json={"disabled": action}, timeout=10.0
                )
                if resp.status_code in [200, 204]:
                    await query.edit_message_text(text=f"✅ Port *{interface_name}* has been {action_text}.")
                else:
                    await query.edit_message_text(text=f"❌ Error: {resp.status_code}")
        except Exception as e:
            await query.edit_message_text(text=f"❌ Error: {e}")

async def start_bot():
    global bot_app
    bot_app = Application.builder().token(TOKEN).request(telegram_request).build()
    bot_app.add_handler(CommandHandler("status", status_command))
    bot_app.add_handler(CommandHandler("logs", logs_command))
    bot_app.add_handler(CommandHandler("mesh", mesh_command))
    bot_app.add_handler(CommandHandler("manage", manage_command))
    bot_app.add_handler(CallbackQueryHandler(button_handler))
    
    await bot_app.initialize()
    await bot_app.start()
    await bot_app.updater.start_polling()
    print("Telegram Bot listener started (Chat-Ops active).")

async def stop_bot():
    if bot_app:
        await bot_app.updater.stop()
        await bot_app.stop()
        await bot_app.shutdown()
