# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import asyncio
from pyrogram import Client, filters
from pyrogram.errors import FloodWait

from info import ADMIN, LOG_CHANNEL  # Make sure ADMIN, LOG_CHANNEL imported
from utils import get_users, get_groups, delete_user, delete_group
import script  # Assuming script.py has BROADCAST string template

@Client.on_message(filters.command('broadcast') & filters.user(ADMIN))
async def broadcast(bot, message):
    if not message.reply_to_message:
        return await message.reply("Use this command as a reply to any message!")

    m = await message.reply("Please wait...")
    count, users = await get_users()
    total = count
    remaining = total
    success = 0
    failed = 0
    br_msg = message.reply_to_message

    for user in users:
        chat_id = user["_id"]
        success_flag = await copy_msgs(br_msg, chat_id)
        if not success_flag:
            failed += 1
        else:
            success += 1
        remaining -= 1

        # Update progress
        try:
            stats = "⚡ Broadcast Processing.."
            await m.edit(script.BROADCAST.format(stats, total, remaining, success, failed))
        except Exception:
            pass

    stats = "✅ Broadcast Completed"
    await m.reply(script.BROADCAST.format(stats, total, remaining, success, failed))
    await m.delete()

    # Optional: log broadcast completion to log channel
    if LOG_CHANNEL:
        await bot.send_message(LOG_CHANNEL, f"Broadcast completed: Success {success}, Failed {failed}")

@Client.on_message(filters.command('broadcast_groups') & filters.user(ADMIN))
async def grp_broadcast(bot, message):
    if not message.reply_to_message:
        return await message.reply("Use this command as a reply to any message!")

    m = await message.reply("Please wait...")
    count, groups = await get_groups()
    total = count
    remaining = total
    success = 0
    failed = 0
    br_msg = message.reply_to_message

    for group in groups:
        chat_id = group["_id"]
        success_flag = await grp_copy_msgs(br_msg, chat_id)
        if not success_flag:
            failed += 1
        else:
            success += 1
        remaining -= 1

        # Update progress
        try:
            stats = "⚡ Broadcast Processing.."
            await m.edit(script.BROADCAST.format(stats, total, remaining, success, failed))
        except Exception:
            pass

    stats = "✅ Broadcast Completed"
    await m.reply(script.BROADCAST.format(stats, total, remaining, success, failed))
    await m.delete()

    if LOG_CHANNEL:
        await bot.send_message(LOG_CHANNEL, f"Group broadcast completed: Success {success}, Failed {failed}")

async def grp_copy_msgs(br_msg, chat_id):
    try:
        msg = await br_msg.copy(chat_id)
        try:
            await msg.pin()
        except Exception:
            pass
        return True
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await grp_copy_msgs(br_msg, chat_id)
    except Exception:
        await delete_group(chat_id)
        return False

async def copy_msgs(br_msg, chat_id):
    try:
        await br_msg.copy(chat_id)
        return True
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await copy_msgs(br_msg, chat_id)
    except Exception:
        await delete_user(chat_id)
        return False
