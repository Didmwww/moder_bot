import asyncio
import logging
from datetime import timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ChatPermissions


TOKEN = "8575171028:AAHTdMlaIvFHg8nFRWqSHHq9uEFRFWUE2RY"  
BAD_WORDS = ["дурень", "спам", "матюк"] 

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()


UNMUTE_PERMISSIONS = ChatPermissions(
    can_send_messages=True,
    can_send_media_messages=True,
    can_send_other_messages=True,
    can_send_polls=True,
    can_add_web_page_previews=True,
    can_invite_users=True
)


MUTE_PERMISSIONS = ChatPermissions(
    can_send_messages=False,
    can_send_media_messages=False,
    can_send_other_messages=False
)

@dp.message(F.new_chat_members)
async def welcome_handler(message: types.Message):
    for new_user in message.new_chat_members:
        if new_user.id == bot.id:
            continue
        

        await message.answer(
            f"Привіт, {new_user.full_name}! 👋\n"
            f"Раді тебе бачити. Ознайомся з правилами в закріпі!"
        )


@dp.message(Command("unmute"))
async def unmute_handler(message: types.Message):
    if not message.reply_to_message:
        await message.reply("Цю команду треба писати у відповідь (reply) на повідомлення користувача, якого треба розмутити.")
        return

    user_status = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if user_status.status not in ['administrator', 'creator']:
        await message.reply("Тільки адміни можуть керувати мутом!")
        return

    user_to_unmute = message.reply_to_message.from_user

    try:
        await bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=user_to_unmute.id,
            permissions=UNMUTE_PERMISSIONS
        )
        await message.reply(f"Користувача {user_to_unmute.full_name} розмучено! ✅")
        
    except Exception as e:
        await message.reply(f"Помилка. Можливо, бот не адмін? Деталі: {e}")


@dp.message(F.text)
async def filter_messages(message: types.Message):
   
    if message.text.startswith('/'):
        return

    text = message.text.lower()
    
    is_link = "http://" in text or "https://" in text or "t.me" in text
    is_profanity = any(word in text for word in BAD_WORDS)

    if is_link or is_profanity:
        try:
            await message.delete()

            await bot.restrict_chat_member(
                chat_id=message.chat.id,
                user_id=message.from_user.id,
                permissions=MUTE_PERMISSIONS,
                until_date=timedelta(hours=1)
            )

            await message.answer(
                f"🚫 {message.from_user.full_name} отримав мут на 1 годину за порушення правил."
            )
        except Exception:
            pass 

async def main():
    print("Бот запущений і готовий вітати...")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    asyncio.run(main())