import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import instaloader

# --- الإعدادات ---
API_TOKEN = '8609584907:AAGrtBOu6anRKW1iSQH3kAJiv4umJUkb1m8'
CHANNEL_ID = '@Ramy_Premium'
CHANNEL_LINK = 'https://t.me/Ramy_Premium'
INSTA_USER = "dragon.4905830"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
L = instaloader.Instaloader()

# --- دالة تحميل الجلسة (السر في النجاح) ---
async def load_insta_session():
    try:
        print(f"🔄 جاري محاولة تحميل جلسة المستخدم: {INSTA_USER}...")
        # يحاول جلب الملف الذي أنشأته أنت يدوياً في الخطوة رقم 1
        await asyncio.to_thread(L.load_session_from_file, INSTA_USER)
        print("✅ تم تحميل الجلسة بنجاح! البوت الآن موثوق لدى إنستغرام.")
    except FileNotFoundError:
        print("❌ لم يتم العثور على ملف الجلسة! يرجى تنفيذ أمر instaloader --login أولاً.")
    except Exception as e:
        print(f"⚠️ خطأ أثناء تحميل الجلسة: {e}")

def sub_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="اضغط هنا للاشتراك في القناة ✅", url=CHANNEL_LINK)]
    ])

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(f"أهلاً بك {message.from_user.first_name}!\nالبوت الآن يعمل بكامل طاقته، أرسل الرابط للتحميل.", reply_markup=sub_kb())

@dp.message()
async def handle_insta(message: types.Message):
    if not message.text or "instagram.com" not in message.text:
        return

    user = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=message.from_user.id)
    if user.status in ['left', 'kicked']:
        return await message.answer("⚠️ يجب الاشتراك أولاً!", reply_markup=sub_kb())

    msg = await message.answer("⏳ جاري سحب الفيديو...")
    try:
        url = message.text
        shortcode = url.split("/")[-2] if url.endswith('/') else url.split("/")[-1]
        shortcode = shortcode.split("?")[0]
        
        # جلب البيانات باستخدام الجلسة المحملة
        post = await asyncio.to_thread(instaloader.Post.from_shortcode, L.context, shortcode)
        
        if post.is_video:
            await message.answer_video(post.video_url, caption="✅ تم التحميل بنجاح")
        else:
            await message.answer_photo(post.url, caption="✅ تم التحميل بنجاح")
        await msg.delete()
    except Exception as e:
        logging.error(e)
        await msg.edit_text("❌ فشل التحميل. قد يكون الفيديو خاصاً أو الرابط غير صحيح.")

async def main():
    await load_insta_session()
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())