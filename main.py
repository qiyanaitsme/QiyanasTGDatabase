import sqlite3
import shutil
import os
import aiogram
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import Document

bot = Bot(token="Тут токен")  # введи сюда токен бота
dp = Dispatcher(bot)

conn = sqlite3.connect("passwords.db")
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS passwords (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        service TEXT,
        email TEXT,
        password TEXT
    )
""")
conn.commit()

allowed_user_ids = [1]  # введи сюда айди пользователей, которым будет доступен функционал бота. Можно несколько людей.

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if message.from_user.id in allowed_user_ids:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["Загрузить данные", "Получить все данные", "Скачать базу данных"]
        keyboard.add(*buttons)
        await message.reply("Привет! Это бот для хранения паролей от Сатары. Чтобы загрузить данные, нажми кнопку 'Загрузить данные'. "
                            "Чтобы получить все данные, нажми кнопку 'Получить все данные'. Чтобы скачать базу данных, нажми кнопку 'Скачать базу данных'.", reply_markup=keyboard)
        await bot.send_photo(message.chat.id, "https://c4.wallpaperflare.com/wallpaper/535/832/930/nier-automata-2b-nier-automata-white-hair-blindfold-wallpaper-preview.jpg")
    else:
        await message.reply("У вас нет доступа к этому боту.")

@dp.message_handler(text='Загрузить данные')
async def upload_data(message: types.Message):
    if message.from_user.id in allowed_user_ids:
        await message.reply("Пожалуйста, отправь сервис:почту:пароль (для массовой загрузки данных, разделите каждую строку новой строкой)")
    else:
        await message.reply("У вас нет доступа к этому боту.")

@dp.message_handler(text='Получить все данные')
async def get_all_data(message: types.Message):
    if message.from_user.id in allowed_user_ids:
        user_id = message.from_user.id
        cursor.execute("SELECT service, email, password FROM passwords WHERE user_id=?", (user_id,))
        data = cursor.fetchall()

        if data:
            response = "Ваши данные:\n\n"
            for row in data:
                service, email, password = row
                response += f"Сервис: {service}\nПочта: {email}\nПароль: {password}\n\n"
            await message.reply(response)
        else:
            response = "У вас нет сохраненных данных."
            await message.reply(response)
    else:
        await message.reply("У вас нет доступа к этому боту.")

@dp.message_handler(text='Скачать базу данных')
async def download_database(message: types.Message):
    if message.from_user.id in allowed_user_ids:
        filename = "passwords.db"
        await bot.send_chat_action(message.chat.id, "upload_document")
        temp_filename = f"temp_{filename}"
        shutil.copyfile(filename, temp_filename)
        with open(temp_filename, 'rb') as document:
            await message.reply_document(document)

        os.remove(temp_filename)
    else:
        await message.reply("У вас нет доступа к этому боту.")

@dp.message_handler()
async def save_data(message: types.Message):
    if message.from_user.id in allowed_user_ids:
        user_id = message.from_user.id
        data = message.text.split('\n')

        for line in data:
            line_data = line.split(':')
            if len(line_data) == 3:
                service, email, password = line_data
                cursor.execute("INSERT INTO passwords (user_id, service, email, password) VALUES (?, ?, ?, ?)",
                               (user_id, service, email, password))
                conn.commit()

        await message.reply("Данные сохранены.")
    else:
        await message.reply("У вас нет доступа к этому боту.")

if __name__ == '__main__':
    executor.start_polling(dp)