import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# --- التكوين الأساسي ---
BOT_TOKEN = "ضع_هنا_API_TOKEN_الخاص_ببوتينك"
WEBSITE_URL = "https://mycima.site"
CHANNEL_USERNAME = "@اسم_قناتك_بدون_علامة_أوت" # مثال: MyCimaChannel

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = f"أهلاً بك يا {user.first_name} في بوت ماي سيما الرسمي! 🎬\n\nاكتب اسم أي فيلم أو مسلسل أبحث لك عنه فوراً."
    await update.message.reply_text(welcome_text)

async def handle_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    user_id = update.effective_user.id
    
    # 1. التحقق من الاشتراك الإجباري بالقناة
    try:
        member = await context.bot.get_chat_member(chat_id=f"@{CHANNEL_USERNAME}", user_id=user_id)
        if member.status in ['left', 'kicked']:
            btn = [[InlineKeyboardButton("📢 اشترك في القناة أولاً", url=f"https://t.me/{CHANNEL_USERNAME}")]]
            await update.message.reply_text(
                "⚠️ يجب عليك الاشتراك في قناة ماي سيما الرسمية أولاً لرؤية رابط الفيلم!",
                reply_markup=InlineKeyboardMarkup(btn)
            )
            return
    except Exception as e:
        pass # في حال عدم رفع البوت أدمن بالقناة بعد

    # 2. البحث في API موقع ماي سيما
    search_url = f"{WEBSITE_URL}/wp-json/wp/v2/posts?search={query}&_embed"
    response = requests.get(search_url)
    
    if response.status_code == 200 and len(response.json()) > 0:
        results = response.json()[:5] # أول 5 نتائج
        for item in results:
            title = item['title']['rendered']
            link = item['link']
            
            keyboard = [[InlineKeyboardButton("🍿 مشاهدة وتحميل على ماي سيما", url=link)]]
            await update.message.reply_text(
                f"🎬 **{title}**\n\nاضغط على الزر بالأسفل للمشاهدة مباشرة بدون إعلانات:",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    else:
        # لو الفيلم مش موجود، نحوله لصفحة البحث العامة بموقعك
        direct_search_link = f"{WEBSITE_URL}/?s={query}"
        keyboard = [[InlineKeyboardButton("🔍 ابحث في موقع ماي سيما", url=direct_search_link)]]
        await update.message.reply_text(
            f"لم نجد نتيجة مباشرة لـ '{query}' داخل البوت، اضغط للبحث داخل الموقع مباشرة:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_search))
    app.run_polling()
