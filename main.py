import asyncio
import logging
import os
import uuid
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiohttp import web
import yt_dlp

# --- الإعدادات الأساسية (تعديلك هنا فقط) ---
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

# --- الأزرار ---
def subscription_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 انضم لقناتنا أولاً", url=CHANNEL_LINK)],
        [InlineKeyboardButton(text="✅ تم الاشتراك، ابدأ الآن", callback_data="check_sub")]
    ])

def store_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 متجر رامي (Netflix/Spotify)", url=CHANNEL_LINK)]
    ])

# --- دالة التحميل ---
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

# --- الأوامر ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if await check_subscription(message.from_user.id):
        await message.answer(f"🌟 أهلاً بك يا {message.from_user.first_name}!\n\nأرسل رابط فيديو (تيك توك، إنستا، فيسبوك) للتحميل فوراً. 🔥", reply_markup=store_keyboard())
    else:
        await message.answer(f"👋 أهلاً بك!\n\nلاستخدام البوت، يجب الاشتراك في القناة أولاً: 👇", reply_markup=subscription_keyboard())

@dp.callback_query(lambda c: c.data == "check_sub")
async def process_check_sub(callback_query: types.CallbackQuery):
    if await check_subscription(callback_query.from_user.id):
        await callback_query.message.edit_text("تم التفعيل! أرسل الرابط الآن. ✅")
    else:
        await callback_query.answer("⚠️ لم تشترك بعد!", show_alert=True)

# --- معالجة الروابط والتحميل ---
@dp.message()
async def handle_links(message: types.Message):
    if not message.text: return
    
    supported = ["tiktok.com", "instagram.com", "facebook.com", "fb.watch"]
    if not any(site in message.text for site in supported):
        return

    if not await check_subscription(message.from_user.id):
        await message.answer("❌ اشترك أولاً:", reply_markup=subscription_keyboard())
        return

    m = await message.answer("⏳ جاري التحميل... انتظر لحظة")
    
    try:
        path = await asyncio.to_thread(download_media, message.text)
        await message.answer_video(
            video=FSInputFile(path),
            caption=f"✅ تم التحميل بنجاح!\n\n🛒 متجر رامي: {CHANNEL_ID}",
            reply_markup=store_keyboard()
        )
        if os.path.exists(path): os.remove(path)
        await m.delete()
    except Exception as e:
        logging.error(e)
        await m.edit_text("❌ خطأ! تأكد أن الحساب عام (Public).")

# --- استقرار Render ---
async def handle(request): return web.Response(text="Bot is Live! ✅")
async def main():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv('PORT', 8080))
    await web.TCPSite(runner, '0.0.0.0', port).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
