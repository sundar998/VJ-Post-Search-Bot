from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# inside f_sub_callback add:
# after successful subscription check:

keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("Get Started ▶️", callback_data=f"start_{user_id}")],
    [InlineKeyboardButton("Verify Token 🔐", url="https://yourlinkshortener.com/api/verify?user_id={user_id}")],
    [InlineKeyboardButton("Buy Premium 💎", url="https://t.me/YourPersonalBot?start=premium")]
])

await update.message.edit(
    "✅ Subscription verified! Please click below to proceed.",
    reply_markup=keyboard
)

# You can also add message auto delete after timer:
await asyncio.sleep(CUSTOM_TIMER_SECONDS)
try:
    await update.message.delete()
except:
    pass
