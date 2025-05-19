# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

from info import *
from utils import *
from plugins.generate import database
from pyrogram import Client, filters

@Client.on_message(filters.group & filters.command("connect"))
async def connect(bot, message):
    m = await message.reply("Connecting..")
    
    # Fetch bot owner session data
    vj = database.find_one({"chat_id": ADMIN})
    if vj is None:
        return await message.reply("**Contact Admin Then Say To Login In Bot.**")

    # Create a client using owner's session (no string session required for users)
    User = Client("post_search", session_string=vj['session'], api_hash=API_HASH, api_id=API_ID)
    await User.connect()

    try:
        group = await get_group(message.chat.id)
        user_id = group["user_id"]
        user_name = group["user_name"]
        verified = group["verified"]
        channels = group["channels"].copy()
    except Exception:
        return await bot.leave_chat(message.chat.id)

    # Permission check: Only the owner of the group can connect channels
    if message.from_user.id != user_id:
        return await m.edit(f"<b>Only {user_name} can use this command</b> 😁")

    # Force subscribe check
    if not verified:
        return await m.edit("💢 <b>This chat is not verified!\n⭕ Use /verify</b>")

    try:
        channel = int(message.command[-1])
    except Exception:
        return await m.edit("❌ <b>Incorrect format!\nUse</b> `/connect ChannelID`")

    # Avoid duplicate connections
    if channel in channels:
        return await message.reply("💢 <b>This channel is already connected! You can't connect again.</b>")

    channels.append(channel)

    try:
        chat = await bot.get_chat(channel)
        group_chat = await bot.get_chat(message.chat.id)
        c_link = chat.invite_link or ""
        g_link = group_chat.invite_link or ""

        # Join the channel using owner's user client
        await User.join_chat(channel)
    except Exception as e:
        if "The user is already a participant" in str(e):
            pass
        else:
            text = (
                f"❌ <b>Error:</b> `{str(e)}`\n"
                f"⭕ <b>Make sure I'm admin in that channel & this group with all permissions "
                f"and {User.me.mention} is not banned there</b>"
            )
            return await m.edit(text)

    # Update DB with new connected channel list
    await update_group(message.chat.id, {"channels": channels})

    await m.edit(f"💢 <b>Successfully connected to [{chat.title}]({c_link})!</b>", disable_web_page_preview=True)

    # Log the new connection to LOG_CHANNEL
    text = f"#NewConnection\n\nUser: {message.from_user.mention}\nGroup: [{group_chat.title}]({g_link})\nChannel: [{chat.title}]({c_link})"
    await bot.send_message(chat_id=LOG_CHANNEL, text=text)


@Client.on_message(filters.group & filters.command("disconnect"))
async def disconnect(bot, message):
    vj = database.find_one({"chat_id": ADMIN})
    if vj is None:
        return await message.reply("**Contact Admin Then Say To Login In Bot.**")

    User = Client("post_search", session_string=vj['session'], api_hash=API_HASH, api_id=API_ID)
    await User.connect()

    m = await message.reply("Please wait..")

    try:
        group = await get_group(message.chat.id)
        user_id = group["user_id"]
        user_name = group["user_name"]
        verified = group["verified"]
        channels = group["channels"].copy()
    except Exception:
        return await bot.leave_chat(message.chat.id)

    if message.from_user.id != user_id:
        return await m.edit(f"Only {user_name} can use this command 😁")

    if not verified:
        return await m.edit("This chat is not verified!\nUse /verify")

    try:
        channel = int(message.command[-1])
    except Exception:
        return await m.edit("❌ <b>Incorrect format!\nUse</b> `/disconnect ChannelID`")

    if channel not in channels:
        return await m.edit("<b>You didn't add this channel yet or check Channel ID</b>")

    channels.remove(channel)

    try:
        chat = await bot.get_chat(channel)
        group_chat = await bot.get_chat(message.chat.id)
        c_link = chat.invite_link or ""
        g_link = group_chat.invite_link or ""

        # Leave channel using owner user client
        await User.leave_chat(channel)
    except Exception as e:
        text = (
            f"❌ <b>Error:</b> `{str(e)}`\n"
            f"💢 <b>Make sure I'm admin in that channel & this group with all permissions "
            f"and {User.me.mention} is not banned there</b>"
        )
        return await m.edit(text)

    await update_group(message.chat.id, {"channels": channels})
    await m.edit(f"💢 <b>Successfully disconnected from [{chat.title}]({c_link})!</b>", disable_web_page_preview=True)

    text = f"#DisConnection\n\nUser: {message.from_user.mention}\nGroup: [{group_chat.title}]({g_link})\nChannel: [{chat.title}]({c_link})"
    await bot.send_message(chat_id=LOG_CHANNEL, text=text)


@Client.on_message(filters.group & filters.command("connections"))
async def connections(bot, message):
    try:
        group = await get_group(message.chat.id)
        user_id = group["user_id"]
        user_name = group["user_name"]
        channels = group["channels"]
        f_sub = group.get("f_sub", None)
    except Exception:
        return await message.reply("Error fetching group info. Make sure this group is registered.")

    if message.from_user.id != user_id:
        return await message.reply(f"<b>Only {user_name} can use this command</b> 😁")

    if not channels:
        return await message.reply("<b>This group is currently not connected to any channels!\nConnect one using /connect</b>")

    text = "This Group is currently connected to:\n\n"
    for channel in channels:
        try:
            chat = await bot.get_chat(channel)
            name = chat.title
            link = chat.invite_link or ""
            text += f"🔗<b>Connected Channel - [{name}]({link})</b>\n"
        except Exception as e:
            await message.reply(f"❌ Error in `{channel}:`\n`{e}`")

    if f_sub:
        try:
            f_chat = await bot.get_chat(f_sub)
            f_title = f_chat.title
            f_link = f_chat.invite_link or ""
            text += f"\nFSub: [{f_title}]({f_link})"
        except Exception as e:
            await message.reply(f"❌ <b>Error in FSub</b> (`{f_sub}`)\n`{e}`")

    await message.reply(text=text, disable_web_page_preview=True)
