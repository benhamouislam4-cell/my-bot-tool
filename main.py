import asyncio
import logging
import os
import uuid
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiohttp import web
import yt_dlp

# --- الإعدادات الأساسية ---
API_TOKEN = '8636877850:AAEDfyWzZgyPZ0QadGmooMM04YiVQan8z1o' 
CHANNEL_ID = '@Ramy_Premium'
CHANNEL_LINK = 'https://t.me/Ramy_Premium'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- دالة التحقق من الاشتراك ---
async def check_subscription(user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ['member', 'creator', 'administrator']
    except:
        return False

# --- لوحة أزرار الاشتراك الإجباري (تصميم جميل) ---
def subscription_keyboard():
    buttons = [
        [InlineKeyboardButton(text="📢 انضم لقناتنا أولاً", url=CHANNEL_LINK)],
        [InlineKeyboardButton(text="✅ تم الاشتراك، ابدأ الآن", callback_data="check_sub")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# --- لوحة أزرار المتجر (تظهر مع الفيديو) ---
def store_keyboard():
    buttons = [
        [InlineKeyboardButton(text="🛒 متجر رامي بريميوم (Netflix/Spotify)", url=CHANNEL_LINK)]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# --- دالة التحميل الذكية ---
def download_media(url):
    unique_filename = f"ramy_dl_{uuid.uuid4().hex}.mp4"
    ydl_opts = {
        'format': 'best',
        'outtmpl': unique_filename,
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
        return unique_filename

# --- معالجة أمر البداية /start ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    is_sub = await check_subscription(message.from_user.id)
    if not is_sub:
        await message.answer(
            f"👋 أهلاً بك يا {message.from_user.first_name}!\n\n"
            "⚠️ لاستخدام البوت وتحميل الفيديوهات من (TikTok, Instagram, Facebook)، "
            "يجب عليك الاشتراك في قناة المتجر الرسمية أولاً. 👇",
            reply_markup=subscription_keyboard()
        )
    else:
        await message.answer(
            f"🌟 أهلاً بك مجدداً!\n\n"
            "قم بإرسال رابط الفيديو الآن وسأقوم بتحميله لك فوراً بأعلى جودة. 🎬🔥",
            reply_markup=store_keyboard()
        )

# --- معالجة زر "تم الاشتراك" ---
@dp.callback_query(lambda c: c.data == "check_sub")
async def process_check_sub(callback_query: types.CallbackQuery):
    if await check_subscription(callback_query.from_user.id):
        await bot.answer_callback_query(callback_query.id, text="شكرًا لانضمامك! تم تفعيل البوت. ✅")
        await bot.send_message(
            callback_query.from_user.id, 
            "تم التحقق بنجاح! 🎉\nأرسل رابط الفيديو الذي تريد تحميله الآن. 👇"
        )
    else:
        await bot.answer_callback_query(
            callback_query.id, 
            text="⚠️ يبدو أنك لم تشترك في القناة بعد، يرجى الانضمام أولاً!", 
            show_alert=True
        )

# --- معالجة الروابط (التحميل الشامل) ---
@dp.message()
async def handle_links(message: types.Message):
    if not message.text: return
    
    # التحقق من أن الرابط مدعوم
    supported_sites = ["tiktok.com", "instagram.com", "facebook.com", "fb.watch"]
    if not any(site in message.text for site in supported_sites):
        return

    # التحقق من الاشتراك قبل التحميل
    if not await check_subscription(message.from_user.id):
        await message.answer("❌ لا يمكنك التحميل! اشترك في القناة أولاً لفتح الخدمة:", reply_markup=subscription_keyboard())
        return

    waiting_msg = await message.answer("⏳ جاري سحب الفيديو من المنصة... انتظر قليلاً")
    
    try:
        video_path = await asyncio.to_thread(download_media, message.text)
        
        await message.answer_video(
            video=FSInputFile(video_path),
            caption=f"✅ تم التحميل بنجاح!\n\n🚀 بواسطة: @{bot.username}\n🛒 متجرنا: {CHANNEL_ID}",
            reply_markup=store_keyboard()
        )
        
        if os.path.exists(video_path):
            os.remove(video_path)
        await waiting_msg.delete()
        
    except Exception as e:
        logging.error(e)
        await waiting_msg.edit_text("❌ عذراً، حدث خطأ أثناء التحميل. تأكد أن الرابط عام وليس لحساب خاص.")

# --- نظام استقرار سيرفر Render ---
async def handle(request):
    return web.Response(text="The Universal Bot is running perfectly! ✅")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv('PORT', 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

async def main():
    asyncio.create_task(start_web_server())
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
