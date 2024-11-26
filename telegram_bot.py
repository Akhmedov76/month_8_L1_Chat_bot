from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from decouple import config
from csv_manager import CsvManager

API_TOKEN = config("API_TOKEN")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

csv_manager = CsvManager("users.csv")


async def on_startup(dispatcher):
    print("Bot ishga tushdi")


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    try:
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        phone_button = KeyboardButton(text="📱 Telefon raqamingizni yuboring", request_contact=True)
        keyboard.add(phone_button)

        await bot.send_message(message.from_user.id, "Botimizga xush kelibsiz! Telefon raqamingizni yuboring:",
                               reply_markup=keyboard)
        await message.delete()
    except Exception as e:
        await bot.send_message(message.from_user.id, f"Xatolik yuz berdi: {e}")


@dp.message_handler(content_types=types.ContentType.CONTACT)
async def handle_contact(message: types.Message):
    try:
        contact = message.contact

        if contact is None or contact.phone_number is None:
            await bot.send_message(message.from_user.id,
                                   "Telefon raqamingizni yuborishda xatolik yuz berdi. Iltimos qayta urinib ko'ring.")
            return

        all_users = csv_manager.read_csv()
        existing_numbers = {user['phone_number'] for user in all_users}
        if contact.phone_number in existing_numbers:
            await bot.send_message(message.from_user.id,
                                   "Bu telefon raqam allaqachon tizimda mavjud! Iltimos boshqa telefon raqamingizni yuboring.")
            return

        user_data = {
            "user_id": message.from_user.id,
            "name": message.from_user.full_name,
            "username": message.from_user.username,
            "phone_number": contact.phone_number
        }
        csv_manager.append_csv(user_data)

        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        view_users_button = KeyboardButton(text="👥 Foydalanuvchilarni ko‘rish")
        keyboard.add(view_users_button)

        await bot.send_message(message.from_user.id, "Telefon raqamingiz saqlandi! Rahmat.", reply_markup=keyboard)
    except Exception as e:
        await bot.send_message(message.from_user.id, f"Xatolik yuz berdi: {e}")


@dp.message_handler(lambda message: message.text == "👥 Foydalanuvchilarni ko‘rish")
async def list_users(message: types.Message):
    try:
        users = csv_manager.read_csv()
        if not users:
            await message.reply("Hozircha hech kim ro'yxatdan o'tmagan.")
            return

        inline_kb = InlineKeyboardMarkup()
        for user in users:
            button_text = f"{user['name']} ({user['phone_number']})"
            callback_data = f"send_message_to_{user['user_id']}"
            inline_kb.add(InlineKeyboardButton(button_text, callback_data=callback_data))

        await message.reply("Ro'yxatdan o'tgan foydalanuvchilar:", reply_markup=inline_kb)
    except Exception as e:
        await message.reply(f"Xatolik yuz berdi: {e}")


@dp.callback_query_handler(lambda c: c.data.startswith("send_message_to_"))
async def send_message_prompt(callback_query: types.CallbackQuery):
    try:
        user_id = callback_query.data.split("_")[-1]
        await bot.send_message(callback_query.from_user.id,
                               "Iltimos, yubormoqchi bo'lgan xabaringizni kiriting:")

        dp.current_user_id = user_id

        dp.register_message_handler(handle_user_message, content_types=types.ContentType.TEXT)
    except Exception as e:
        await bot.send_message(callback_query.from_user.id, f"Xatolik yuz berdi: {e}")


async def handle_user_message(message: types.Message):
    try:
        user_id = dp.current_user_id

        await bot.send_message(user_id, f"Yangi xabar: {message.text}")

        await message.reply("Xabar muvaffaqiyatli yuborildi!")

    except Exception as e:
        await message.reply(f"Xabar yuborishda xatolik yuz berdi: {e}")


if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
