"""Enable Seen Counter in any message,
to know how many users have seen your message
Syntax: .fwd as reply to any message"""
from telethon import events
from userbot.utils import admin_cmd


@borg.on(admin_cmd("fwd"))
async def _(event):
    if event.fwd_from:
        return
    if Config.PRIVATE_GROUP_BOT_API_ID is None:
        await event.edit("Enter PRIVATE_GROUP_BOT_API_ID In Heroku")
        return False
    try:
        e = await borg.get_entity(int(Config.PRIVATE_GROUP_BOT_API_ID))
    except Exception as e:
        await event.edit(str(e))
    else:
        re_message = await event.get_reply_message()
        # https://t.me/telethonofftopic/78166
        fwd_message = await borg.forward_messages(
            e,
            re_message,
            silent=True
        )
        await borg.forward_messages(
            event.chat_id,
            fwd_message
        )
        await fwd_message.delete()
        await event.delete()
