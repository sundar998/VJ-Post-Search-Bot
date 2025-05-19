# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import traceback
from pyrogram.types import Message
from pyrogram import Client, filters
from asyncio.exceptions import TimeoutError
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import (
    ApiIdInvalid,
    PhoneNumberInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    PasswordHashInvalid
)
from info import API_ID, API_HASH, DATABASE_URI, ADMIN
from pymongo import MongoClient

mongo_client = MongoClient(DATABASE_URI)
database = mongo_client.userdb.sessions

strings = {
    'need_login': "You have to /login before using the bot to download restricted content ❕",
    'already_logged_in': "You are already logged in.\nIf you want to login again, please use /logout to proceed.",
}
SESSION_STRING_SIZE = 351  # Minimum expected length for valid session strings

def get(obj, key, default=None):
    try:
        return obj[key]
    except:
        return default

@Client.on_message(filters.private & filters.command(["logout"]) & filters.user(ADMIN))
async def logout(_, msg: Message):
    user_data = database.find_one({"chat_id": msg.chat.id})
    if user_data is None or not user_data.get('session'):
        return await msg.reply("You are not logged in.")
    data = {
        'session': None,
        'logged_in': False
    }
    database.update_one({'_id': user_data['_id']}, {'$set': data})
    await msg.reply("**Logout Successfully** ♦")

@Client.on_message(filters.private & filters.command(["login"]) & filters.user(ADMIN))
async def main(bot: Client, message: Message):
    user_data = database.find_one({"chat_id": message.from_user.id})
    if get(user_data, 'logged_in', False):
        await message.reply(strings['already_logged_in'])
        return

    user_id = int(message.from_user.id)

    # Step 1: Ask for phone number
    phone_number_msg = await bot.ask(
        chat_id=user_id, 
        text=(
            "<b>Please send your phone number including country code</b>\n"
            "<b>Example:</b> <code>+13124562345, +9171828181889</code>"
        )
    )
    if phone_number_msg.text == '/cancel':
        return await phone_number_msg.reply('<b>Process cancelled!</b>')

    phone_number = phone_number_msg.text

    client = Client(":memory:", API_ID, API_HASH)
    await client.connect()

    await phone_number_msg.reply("Sending OTP...")

    try:
        code = await client.send_code(phone_number)
    except PhoneNumberInvalid:
        await phone_number_msg.reply('`PHONE_NUMBER` **is invalid.**')
        await client.disconnect()
        return

    # Step 2: Ask for OTP code
    phone_code_msg = await bot.ask(
        user_id, 
        (
            "Please check for an OTP in the official Telegram account. "
            "If you got it, send OTP here after reading the format below.\n\n"
            "If OTP is `12345`, **please send it as** `1 2 3 4 5`.\n\n"
            "**Enter /cancel to cancel the process**"
        ), 
        filters=filters.text, 
        timeout=600
    )
    if phone_code_msg.text == '/cancel':
        await client.disconnect()
        return await phone_code_msg.reply('<b>Process cancelled!</b>')

    try:
        phone_code = phone_code_msg.text.replace(" ", "")
        await client.sign_in(phone_number, code.phone_code_hash, phone_code)
    except PhoneCodeInvalid:
        await phone_code_msg.reply('**OTP is invalid.**')
        await client.disconnect()
        return
    except PhoneCodeExpired:
        await phone_code_msg.reply('**OTP is expired.**')
        await client.disconnect()
        return
    except SessionPasswordNeeded:
        # Two-step verification password required
        two_step_msg = await bot.ask(
            user_id,
            '**Your account has two-step verification enabled. Please provide the password.\n\nEnter /cancel to cancel the process**',
            filters=filters.text,
            timeout=300
        )
        if two_step_msg.text == '/cancel':
            await client.disconnect()
            return await two_step_msg.reply('<b>Process cancelled!</b>')

        try:
            password = two_step_msg.text
            await client.check_password(password=password)
        except PasswordHashInvalid:
            await two_step_msg.reply('**Invalid Password Provided**')
            await client.disconnect()
            return

    # Export and save session string
    string_session = await client.export_session_string()
    await client.disconnect()

    if len(string_session) < SESSION_STRING_SIZE:
        return await message.reply('<b>Invalid session string</b>')

    try:
        if user_data is not None:
            data = {
                'session': string_session,
                'logged_in': True
            }

            uclient = Client(":memory:", session_string=data['session'], api_id=API_ID, api_hash=API_HASH)
            await uclient.connect()
            # You might add test calls here if needed
            await uclient.disconnect()

            database.update_one({'_id': user_data['_id']}, {'$set': data})
        else:
            # Insert new user if none found
            database.insert_one({
                'chat_id': message.from_user.id,
                'session': string_session,
                'logged_in': True
            })

    except Exception as e:
        return await message.reply_text(f"<b>ERROR IN LOGIN:</b> `{e}`")

    await bot.send_message(message.from_user.id, "<b>Account Login Successfully.\n\nIf you get any AUTH KEY errors, try /logout and then /login again</b>")
