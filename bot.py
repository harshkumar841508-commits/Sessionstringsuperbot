import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

# ========================
# FIXED USER VARIABLES
# ========================
API_ID = 24916176
API_HASH = "15e8847a5d612831b6a42c5f8d846a8a"
BOT_TOKEN = "8296735009:AAFZ0kD-6e2bayRxSasUOO_DUS-GXYjtiZU"

bot = Client(
    "session_gen_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Temporary user storage
user_data = {}


@bot.on_message(filters.command("start") & filters.private)
async def start_cmd(c, m: Message):
    await m.reply(
        "**Welcome to Pyrogram Session Generator Bot 🔐**\n\n"
        "📲 *Send your phone number with country code*\n"
        "Example: `+919876543210`\n\n"
        "Bot will generate: **Pyrogram Session String (v2)**"
    )


@bot.on_message(filters.private)
async def generator(c, m: Message):
    text = m.text.strip()

    # STEP 1 → PHONE NUMBER
    if text.startswith("+") and text[1:].isdigit():
        phone = text
        user_data[m.from_user.id] = {"phone": phone}

        await m.reply("📨 **Sending OTP... Please wait 5 seconds!**")

        async def send_code():
            user = Client(
                f"temp_{m.from_user.id}",
                api_id=API_ID,
                api_hash=API_HASH
            )
            await user.connect()
            sent = await user.send_code(phone)

            user_data[m.from_user.id]["client"] = user
            user_data[m.from_user.id]["sent"] = sent

            await m.reply("✅ OTP sent!\nNow send the **OTP code** like: `12345`")

        await asyncio.create_task(send_code())
        return

    # STEP 2 → OTP CODE
    if m.from_user.id in user_data and "client" in user_data[m.from_user.id]:
        code = text

        data = user_data[m.from_user.id]
        phone = data["phone"]
        sent = data["sent"]
        user: Client = data["client"]

        try:
            await user.sign_in(phone, sent.phone_code_hash, code)
        except:
            await m.reply("🔐 Your Telegram has **2FA Password**\nSend your password now.")
            user_data[m.from_user.id]["need_password"] = True
            return

        session = await user.export_session_string()
        await user.disconnect()

        await m.reply(
            "**🎉 Session String Generated Successfully!**\n\n"
            f"`{session}`\n\n"
            "⚠ Save it safely. Do NOT share it with anyone."
        )

        user_data.pop(m.from_user.id, None)
        return

    # STEP 3 → PASSWORD (2FA)
    if m.from_user.id in user_data and user_data[m.from_user.id].get("need_password"):
        password = text
        data = user_data[m.from_user.id]
        phone = data["phone"]
        sent = data["sent"]
        user: Client = data["client"]

        try:
            await user.sign_in(
                phone,
                sent.phone_code_hash,
                password=password
            )
        except Exception as e:
            return await m.reply(f"❌ Wrong Password: {e}")

        session = await user.export_session_string()
        await user.disconnect()

        await m.reply(
            "**🎉 Session String Generated with Password!**\n\n"
            f"`{session}`"
        )

        user_data.pop(m.from_user.id, None)
        return


print("🔥 SESSION GENERATOR BOT STARTED 🔥")
bot.run()
